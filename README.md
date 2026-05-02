# Meetbot Demo

Goal: build a bot that:

- Joins a Google Meet call
- Shares a screen of a product
- Talks to you to understand your needs
- Walks you through the product and how it can help you

## What works now

`main.py` creates a Google Meet space through the Google Meet REST API and prints
the Meet join URL.

The REST API can create/manage meeting spaces and inspect conference metadata,
but it is not the same thing as a participant bot. A bot that joins a live call
and handles realtime audio/video needs the Google Meet Media API, which is
currently a Developer Preview flow with additional enrollment and policy
requirements.

## Setup

1. Enable the Google Meet API in a Google Cloud project.
2. Configure the Google Auth consent screen for that project.
3. Create an OAuth 2.0 client:
   - Application type: `Desktop app`
   - Download the JSON file into this directory as `credentials.json`
4. Copy the env template:

   ```bash
   cp .env.example .env
   ```

5. Install dependencies and run:

   ```bash
   uv sync
   uv run python main.py
   ```

On the first run, the program opens a browser for Google OAuth consent. After
you approve the requested Meet scope, it writes `token.json` locally and reuses
that token on later runs.

## How auth works

Google Meet REST API calls run as a Google user, not as an anonymous API key.
For this local demo, the app uses an OAuth 2.0 Desktop client:

- `credentials.json` identifies this app to Google's OAuth server. It is not the
  user's access token, but it should still stay out of git.
- The browser login proves which Google user is authorizing the app.
- The scope in `.env` controls what the app is asking permission to do. This demo
  only requests `https://www.googleapis.com/auth/meetings.space.created`, which
  allows it to create and manage Meet spaces created by the app.
- `token.json` is created after consent. It contains the user's OAuth access and
  refresh tokens, so it must stay private and out of git.
- If you change `GOOGLE_MEET_SCOPES`, delete `token.json` and run again so Google
  can ask for the new permissions.

Official docs:

- [Google Meet Python quickstart](https://developers.google.com/workspace/meet/api/guides/quickstart/python)
- [Authenticate and authorize Meet REST API requests](https://developers.google.com/workspace/meet/api/guides/authenticate-authorize)
- [Meet Media API overview](https://developers.google.com/workspace/meet/media-api/guides/overview)
