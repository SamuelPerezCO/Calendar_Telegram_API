from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

ROOT = Path(__file__).parents[2]
CREDENTIALS_FILE = str(ROOT / "credentialsCalendar.json")  
TOKEN_FILE = str(ROOT / "token.json")                      
_service = None


def get_calendar_service():
    global _service
    if _service is None:
        creds = None

        if Path(TOKEN_FILE).exists():
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:

                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())

        _service = build("calendar", "v3", credentials=creds)
    return _service


def create_event(title, start, end, description=None):
    event = {
        "summary": title,  
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }
    if description:
        event["description"] = description

    return get_calendar_service().events().insert(calendarId="primary", body=event).execute()
