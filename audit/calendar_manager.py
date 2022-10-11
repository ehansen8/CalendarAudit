from dateutil.relativedelta import relativedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .models import *
from .event_builder import EventBuilder
from .utils import *
import uuid
from googleapiclient.errors import HttpError


class CalendarManager:
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    WATCH_URL = "https://7680-24-121-68-47.ngrok.io/audit/watch/"
    FIELDS = "items(id,status,summary,eventType,start,end,organizer,attendees(email,responseStatus)),nextPageToken,nextSyncToken"

    def __init__(self, user: User, watch_config=True) -> None:
        self.user = user
        self.creds = self._get_creds()
        self.service = build("calendar", "v3", credentials=self.creds)
        self.calendar = self._config_user()
        if watch_config:
            self._config_watch()

    def _get_creds(self):
        """Builds the credentials of a user and or refreshes them as needed"""
        creds = None

        if self.user.auth_token:
            creds = Credentials.from_authorized_user_info(
                self.user.auth_info, self.SCOPES
            )

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                creds = flow.r

            # Save the credentials for the next run
            self.user.auth_token = creds.to_json()
            self.user.save()

        return creds

    def _config_user(self) -> Calendar:
        """Configures a users Primary Calendar if not setup"""
        if self.user.primary_calendar:
            return self.user.primary_calendar

        primary = self.service.calendars().get(calendarId="primary").execute()
        self.user.primary_calendar, _ = Calendar.objects.get_or_create(
            email=primary["id"], timezone=primary["timeZone"]
        )

        self.user.save()

        return primary

    def _config_watch(self):
        """Checks if the watch channel for the users Primary Calendar exists and is valid,
        otherwise creates a new watch channel
        """

        try:
            channel = self.user.primary_calendar.channel
        except WatchChannel.DoesNotExist:
            pass
        else:
            if channel.is_valid():
                return
            # Delete channel if it is expired
            channel.delete()

        self._start_watch()

    def sync_events(self, full_sync=False):
        cal = self.calendar

        if full_sync:
            cal.sync_token = None
            cal.save()
            cal.events.all().delete()
        try:
            events = self._get_events()

        except HttpError as error:
            #SyncToken is corrupted -> clear db and re-sync
            if error.status_code == 410:
                self.sync_events(full_sync=True)
                return

        EventBuilder(self.user).save_events(events)

    def _get_events(self) -> list[dict]:
        """Return events via sync token"""
        cal = self.calendar
        events = []
        page_token = None
        # Loop through all pages of sync until nextPageToken is empty
        while True:
            results = (
                self.service.events()
                .list(
                    calendarId="primary",
                    maxResults=2500,
                    singleEvents=True,
                    syncToken=cal.sync_token,
                    pageToken=page_token,
                    fields=self.FIELDS
                )
                .execute()
            )
            events.extend(results.get("items", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                cal.sync_token = results.get("nextSyncToken")
                cal.save()
                break

        return events

    def _start_watch(self):

        calendar = self.user.primary_calendar
        address = self.WATCH_URL
        id = uuid.uuid1()
        body = {
            "id": str(id),
            "type": "webhook",
            "address": address,
            "token": calendar.email,
        }
        results = (
            self.service.events().watch(calendarId=calendar.email, body=body).execute()
        )
        resource_id = results.get("resourceId")
        expiration = int(results.get("expiration")) // 1000  # Convert to seconds
        channel = WatchChannel.objects.create(
            id=id,
            resource_id=resource_id,
            expiration=datetime.fromtimestamp(expiration),
            calendar=calendar,
        )

    def stop_watch(self, channel_id=None, resource_id=None):
        body = {
            "id": channel_id,
            "resourceId": resource_id,
        }
        res = self.service.channels().stop(body=body).execute()
        return res

    # Testing Only Methods
    def __scan_events_in_range(self, months_behind, months_ahead):
        """DEPRECATED: Gets all events in range and attempts to save them if they aren't in the db"""
        tz = self.user.primary_calendar.timezone
        this_month = DateUtil(tz=tz).this_month
        max_range = this_month + relativedelta(months=months_ahead)
        min_range = this_month - relativedelta(months=months_behind)
        events = self.__get_events_by_range(min_range, max_range)
        EventBuilder(self.user).save_events(events)

    def __get_events_by_range(self, min_range, max_range) -> list[dict]:
        """DEPRECATED: Return events from a range"""
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=to_rfc(min_range),
                timeMax=to_rfc(max_range),
                maxResults=2500,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])
