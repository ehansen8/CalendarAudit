from unittest.util import _MAX_LENGTH
import black
from django.db import models
from datetime import datetime, timezone
from django.contrib.auth.models import AbstractUser
import json


class Calendar(models.Model):
    email = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255, blank=True, null=True)
    sync_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.email


class WatchChannel(models.Model):
    id = models.UUIDField(primary_key=True)
    resource_id = models.CharField(max_length=255)
    expiration = models.DateTimeField()
    calendar = models.OneToOneField(
        Calendar,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="channel",
    )

    def is_valid(self) -> bool:
        if self.expiration >= datetime.now(timezone.utc):
            return True
        return False


class User(AbstractUser):
    auth_token = models.JSONField(blank=True, null=True)
    primary_calendar = models.OneToOneField(
        Calendar, on_delete=models.PROTECT, blank=True, null=True
    )

    @property
    def auth_info(self):
        return json.loads(self.auth_token)


class Attendee(models.Model):
    calendar = models.ForeignKey(
        Calendar, on_delete=models.CASCADE, related_name="attendance"
    )
    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="attendance"
    )
    response_status = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.calendar} - {self.event}"


class Event(models.Model):

    google_id = models.CharField(max_length=255)
    calendars = models.ManyToManyField(Calendar, related_name="events")

    organizer = models.ForeignKey(
        Calendar, on_delete=models.CASCADE, related_name="organized_events"
    )

    status = models.CharField(max_length=9)
    summary = models.CharField(max_length=255, blank=True, null=True)
    event_type = models.CharField(max_length=11)
    all_day = models.BooleanField(default=False)

    start = models.DateTimeField()
    duration = models.DurationField()

    attendees = models.ManyToManyField(
        Calendar, through=Attendee, related_name="attended_events"
    )

    def __str__(self) -> str:
        return f"{self.summary}: {self.start}"
