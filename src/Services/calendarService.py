from pathlib import Path

# Request: used to refresh an expired token without asking you to log in again
from google.auth.transport.requests import Request
# Credentials: represents a saved login (the content of token.json)
from google.oauth2.credentials import Credentials
# InstalledAppFlow: runs the one-time browser login using your app's identity
from google_auth_oauthlib.flow import InstalledAppFlow
# build: creates the client object used to call the Calendar API
from googleapiclient.discovery import build

# The permission we ask Google for: full read/write access to your calendars.
# If you change this list, delete token.json so the login runs again with the new permission.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Build absolute paths from this file's location: Services -> src -> project root.
# This way the bot finds the files no matter which folder you run it from.
ROOT = Path(__file__).parents[2]
CREDENTIALS_FILE = str(ROOT / "credentialsCalendar.json")  # your app's identity (downloaded from Google Cloud, never modified)
TOKEN_FILE = str(ROOT / "token.json")                      # your personal login (created by this code after the first sign-in)

# Cache: we build the connection once and reuse it for every Telegram message,
# instead of rebuilding it on each button press.
_service = None


def get_calendar_service():
    global _service
    if _service is None:
        creds = None

        # Step 1: if we already logged in before, load the saved login from token.json
        if Path(TOKEN_FILE).exists():
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # Step 2: no saved login, or it's no longer valid -> we need to get one
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # The token expired but Google gave us a "refresh token":
                # exchange it for a new one silently, no browser needed.
                creds.refresh(Request())
            else:
                # First time ever: open the browser so you log in with your gmail
                # and accept the permissions. port=0 means "use any free port".
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Step 3: save the login to token.json so next runs skip the browser
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())

        # Step 4: build the client. "calendar" + "v3" = the Google Calendar API v3.
        _service = build("calendar", "v3", credentials=creds)
    return _service


def create_event(title, start, end, description=None):
    # The event is sent to Google as a dictionary with the fields the API expects:
    # https://developers.google.com/calendar/api/v3/reference/events/insert
    event = {
        "summary": title,  # the title shown in the calendar
        # isoformat() turns the datetime into the text format Google requires,
        # including your timezone offset, e.g. "2026-07-19T15:00:00-05:00"
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }
    if description:
        event["description"] = description

    # calendarId="primary" = the main calendar of the logged-in account.
    # execute() actually sends the HTTP request and returns the created event
    # as a dictionary (including "htmlLink", a URL to open it in Google Calendar).
    return get_calendar_service().events().insert(calendarId="primary", body=event).execute()
