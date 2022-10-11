from django.test import TestCase
import pytz
from .utils import to_dt
from datetime import datetime
from .models import *
from .event_builder import EventBuilder

# Create your tests here.
class RfcConversionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rfc_datetime = "2022-01-01T00:00:00-70:00"
        cls.rfc_date = "2022-01-01"
        cls.tz = "America/Phoenix"
        cls.output = pytz.timezone(cls.tz).localize(datetime(year=2022, month=1, day=1))

    def test_convert_date(self):
        date_test = to_dt(self.rfc_date, tz=self.tz, as_date=True)
        self.assertEqual(date_test, self.output)

    def test_convert_datetime(self):
        datetime_test = to_dt(self.rfc_datetime, tz=self.tz)
        self.assertEqual(datetime_test, self.output)


# Create your tests here.
class EventBuilderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event_data = {
            "id": 1,
            "status": "confirmed",
            "summary": "Test Event",
            "eventType": "default",
            "start": {"dateTime": "2022-01-01T00:00:00-70:00"},
            "end": {"dateTime": "2022-01-01T12:00:00-70:00"},
            "organizer": {"email": "ehansen8@wisc.edu"},
            "attendees": [
                {"email": "ehansen8@wisc.edu", "responseStatus": "accepted"},
                {"email": "testuser@wisc.edu", "responseStatus": "accepted"},
            ],
        }
        pc= Calendar(email="ehansen8@wisc.edu", timezone="America/Phoenix")
        pc.save()
        user = User(primary_calendar=pc)
        EventBuilder(user=user).save_event(event_data=cls.event_data)

    def test_event_exists(self):
        try:
            event = Event.objects.get(google_id=self.event_data["id"])
        except Event.DoesNotExist:
            self.fail("event does not exist")
