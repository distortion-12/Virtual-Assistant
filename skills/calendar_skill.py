import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    # This assumes the same token.json from the email skill can be used if scopes are compatible
    # For simplicity, we are reusing it. In a real app, you might manage tokens separately.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_daily_briefing() -> str:
    """Gets today's calendar events."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=5, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return "You have no upcoming events on your calendar."
        
        briefing = "Here's your daily briefing. "
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            time = datetime.datetime.fromisoformat(start).strftime('%I:%M %p')
            briefing += f"At {time}, you have {event['summary']}. "
        return briefing
    except Exception as e:
        print(f"Calendar Error: {e}")
        return "I had trouble accessing your calendar. You may need to authorize me first."