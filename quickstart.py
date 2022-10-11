from __future__ import print_function

from datetime import datetime, time
import pytz
from dateutil.relativedelta import relativedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow()
        now_str = now.isoformat() + "Z"  # 'Z' indicates UTC

        delta = relativedelta(months=3)
        offset = now - delta
        offset_str = offset.isoformat() + "Z"

        print("Getting all events in the last 3 months")
        print(now)
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMax=now_str,
                timeMin=offset_str,
                maxResults=2500,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        tz = pytz.timezone(events_result["timeZone"])

        for event in events:
            # Gets datetime else default to date for allday events
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            s = datetime.strptime(start[:-6], "%Y-%m-%dT%H:%M:%S")
            e = datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S")
            s_t = tz.localize(s)
            e_t = tz.localize(e)
            diff = e - s
            print(s_t, e_t, diff, event["summary"])

        print("Total results:", len(events))
    except HttpError as error:
        print("An error occurred: %s" % error)


if __name__ == "__main__":
    main()
