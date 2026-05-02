from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from google.apps import meet_v2
from google.auth.credentials import Credentials
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow


def _load_credentials(scopes: list[str]) -> Credentials:
    client_secrets_file_json = base64.b64decode(os.environ["GOOGLE_OAUTH_CLIENT_SECRETS_FILE_BASE64"])
    token_file = Path("/tmp/meetbot_token.json")

    creds = None
    if token_file.exists():
        creds = OAuthCredentials.from_authorized_user_file(str(token_file), scopes)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_config(json.loads(client_secrets_file_json), scopes)
        creds = flow.run_local_server(port=0)

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json(), encoding="utf-8")

    return creds


def create_meet() -> tuple[str, str]:
    scopes = ["https://www.googleapis.com/auth/meetings.space.created"]

    try:
        creds = _load_credentials(scopes)
        client = meet_v2.SpacesServiceClient(credentials=creds)
        response = client.create_space(request=meet_v2.CreateSpaceRequest())
    except (FileNotFoundError, GoogleAuthError, ValueError) as error:
        raise SystemExit(f"Google Meet setup failed:\n{error}") from error

    return response.meeting_uri, response.name
