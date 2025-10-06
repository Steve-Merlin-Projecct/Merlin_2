import json
import os

# Get the credentials from environment
creds_json = os.environ["GOOGLE_CREDENTIALS"]
creds_dict = json.loads(creds_json)

# Use with Google libraries
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_config(creds_dict, ["https://www.googleapis.com/auth/gmail.readonly"])
