import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# Scopes define the level of access you are requesting
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
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
    return build('gmail', 'v1', credentials=creds)

def read_latest_email() -> str:
    """Reads the latest unread email from the inbox."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return "You have no new emails."
        
        msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
        payload = msg['payload']
        headers = payload['headers']
        
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        
        return f"Latest email from {sender}. Subject: {subject}."
    except Exception as e:
        print(f"Email Error: {e}")
        return "I had trouble accessing your email. You may need to authorize me first."