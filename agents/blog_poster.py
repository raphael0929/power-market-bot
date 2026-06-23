"""Google Blogger API v3를 통해 Blogspot에 글을 게시합니다."""
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger"]


def _get_credentials() -> Credentials:
    data = json.loads(os.environ["BLOGGER_OAUTH2_TOKEN"])
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


def post_to_blogger(title: str, html_content: str, labels: list) -> str:
    """Blogspot에 포스트를 게시하고 URL을 반환합니다."""
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    creds = _get_credentials()
    service = build("blogger", "v3", credentials=creds)

    body = {"title": title, "content": html_content, "labels": labels}
    result = (
        service.posts()
        .insert(blogId=blog_id, body=body, isDraft=False)
        .execute()
    )
    return result.get("url", "")
