#!/usr/bin/env python3
"""
Google OAuth2 인증 토큰 초기 설정 스크립트 (로컬에서 1회만 실행)

사전 준비:
  1. Google Cloud Console → API 및 서비스 → OAuth 2.0 클라이언트 ID
     - 유형: 데스크톱 앱
     - Blogger API v3, YouTube Data API v3 사용 설정 필요
  2. 다운로드한 JSON 파일을 client_secrets.json 으로 저장
  3. python setup_auth.py 실행
  4. 브라우저에서 Google 계정 인증
  5. 출력된 JSON 두 개를 GitHub Secrets에 등록:
     - BLOGGER_OAUTH2_TOKEN
     - YOUTUBE_OAUTH2_TOKEN
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SECRETS_FILE = "client_secrets.json"


def setup_scope(scopes: list, label: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {label} 인증")
    print(f"{'='*50}")
    flow = InstalledAppFlow.from_client_secrets_file(SECRETS_FILE, scopes)
    creds = flow.run_local_server(port=0)
    data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }
    print(f"\n✅ {label} 시크릿 값 (GitHub Secrets에 등록):")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    print("Google API OAuth2 설정을 시작합니다.")
    print("브라우저 창이 열리면 Google 계정으로 로그인하세요.\n")

    setup_scope(
        ["https://www.googleapis.com/auth/blogger"],
        "BLOGGER_OAUTH2_TOKEN"
    )
    setup_scope(
        ["https://www.googleapis.com/auth/youtube.upload"],
        "YOUTUBE_OAUTH2_TOKEN"
    )

    print("\n✅ 설정 완료! 위 JSON 값들을 GitHub Secrets에 등록하세요.")
    print("   Settings → Secrets and variables → Actions → New repository secret")
