import audit.utils as utils
from .models import Calendar, Event, Attendee, User
from django.db import connection, transaction


class EventBuilder:
    def __init__(self, user: User) -> None:
        self.calendar = user.primary_calendar

    def save_events(self, events_list: list[dict]) -> None:
        for event_data in events_list:
            event = Event()
            g_id = event_data["id"]
            status = event_data["status"]
            if Event.objects.filter(google_id=g_id).exists():
                event = Event.objects.get(google_id=g_id)

                # The event has been deleted and should be removed from the db
                if status == "cancelled":
                    event.delete()
                    continue

                # If it doesn't exist for this user -> add it
                if event.calendars.filter(email=self.calendar.email).exists():
                    event.calendars.add(self.calendar)
                    continue
                
            if status == "cancelled":
                continue
            self.save_event(event_data, base_event=event)


    @transaction.atomic
    def save_event(self, event_data: dict, base_event: Event = None) -> None:
        '''Saves an event from the given event data. Can also take an existing event to update'''
        event = Event()
        if base_event:
            event = base_event

        event.google_id = event_data.get("id")
        event.status = event_data.get("status")
        event.summary = event_data.get("summary")
        event.event_type = event_data.get("eventType")
        self._set_event_times(event, event_data)
        self._set_event_organizer(event, event_data.get("organizer", None))

        # Save before adding many-many
        event.save()

        # Only add to event if not already added (for overwriting purposes)
        if not event.calendars.filter(pk=self.calendar.pk).exists():
            event.calendars.add(self.calendar)

        self._set_event_attendees(event, event_data.get("attendees", []))

    def _set_event_times(self, event: Event, event_data: dict) -> None:
        start = end = None
        as_date = False
        tz = self.calendar.timezone
        if "dateTime" in event_data["start"]:
            start = event_data["start"]["dateTime"]
            end = event_data["end"]["dateTime"]
            event.all_day = False
        else:
            start = event_data["start"]["date"]
            end = event_data["end"]["date"]
            as_date = True
            event.all_day = True

        start = utils.to_dt(start, tz=tz, as_date=as_date)
        end = utils.to_dt(end, tz=tz, as_date=as_date)

        event.start = start
        event.duration = end - start

    def _set_event_organizer(self, event: Event, organizer: dict) -> None:
        if organizer:
            event.organizer, _ = Calendar.objects.get_or_create(email=organizer["email"])

    def _set_event_attendees(self, event: Event, attendees: dict) -> None:
        if not attendees:
            return
        to_set = []
    
        for attendee in attendees:
            calendar, _ = Calendar.objects.get_or_create(email=attendee["email"])
            to_set.append(
                Attendee(calendar=calendar, response_status=attendee["responseStatus"])
            )
        
        # If overwriting, all the intermediary models need to be deleted and re-added
        event.attendance.all().delete()
        event.attendance.set(to_set, bulk=False)
