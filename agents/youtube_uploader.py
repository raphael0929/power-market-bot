"""YouTube Data API v3로 Shorts 영상을 업로드합니다."""
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB


def _get_credentials() -> Credentials:
    data = json.loads(os.environ["YOUTUBE_OAUTH2_TOKEN"])
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=SCOPES,
    )
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def upload_youtube_short(
    video_path: str, title: str, description: str, tags: list
) -> str:
    """YouTube Shorts를 업로드하고 URL을 반환합니다."""
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description + "\n\n#Shorts",
            "tags": (tags or []) + ["Shorts"],
            "categoryId": "22",
            "defaultLanguage": "ko",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path, mimetype="video/mp4", resumable=True, chunksize=CHUNK_SIZE
    )
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]
    return f"https://www.youtube.com/shorts/{video_id}"
