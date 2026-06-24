#!/usr/bin/env python3
"""
매일 블로그 글 게재 + YouTube Shorts 업로드 에이전트

사용법:
  python daily_agent.py generate   # 초안 생성 → drafts/ 저장
  python daily_agent.py publish    # drafts/ 또는 approved/ → Blogger + YouTube 게시
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DRAFTS_DIR = Path("drafts")
APPROVED_DIR = Path("approved")
PUBLISHED_DIR = Path("published")


def cmd_generate() -> None:
    """오늘의 초안을 생성하고 drafts/ 폴더에 저장합니다."""
    from agents.content_generator import generate_daily_content

    topic = os.environ.get("INPUT_TOPIC") or None
    print("📝 콘텐츠 초안 생성 중...")
    content = generate_daily_content(topic=topic)

    DRAFTS_DIR.mkdir(exist_ok=True)
    out_path = DRAFTS_DIR / f"{content['date']}.json"
    out_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ 초안 저장 완료: {out_path}")
    print(f"   블로그 제목 : {content['blog']['title']}")
    print(f"   YouTube 제목: {content['youtube']['title']}")


def cmd_publish() -> None:
    """초안 또는 승인된 파일을 Blogger와 YouTube에 게시합니다."""
    from agents.blog_poster import post_to_blogger
    from agents.video_creator import create_shorts_video
    from agents.youtube_uploader import upload_youtube_short

    # CONTENT_FILE 환경변수 우선, 없으면 approved/ → drafts/ 순서로 탐색
    content_file = os.environ.get("CONTENT_FILE")
    if content_file:
        target = Path(content_file)
    else:
        today = date.today().isoformat()
        target = APPROVED_DIR / f"{today}.json"
        if not target.exists():
            target = DRAFTS_DIR / f"{today}.json"

    if not target.exists():
        print(f"⚠️ 게시할 파일이 없습니다: {target}")
        sys.exit(0)

    print(f"📂 게시 파일: {target}")
    content = json.loads(target.read_text(encoding="utf-8"))
    today = content["date"]
    blog = content["blog"]
    yt = content["youtube"]

    # ── 1. Blogspot 게시 ──────────────────────────────────────
    print("📖 Blogspot 게시 중...")
    blog_url = post_to_blogger(
        title=blog["title"],
        html_content=blog["html_content"],
        labels=blog.get("labels", []),
    )
    print(f"   ✅ {blog_url}")

    # ── 2. YouTube Shorts 생성 + 업로드 ──────────────────────
    print("🎬 YouTube Shorts 영상 생성 중...")
    video_path = f"/tmp/shorts_{today}.mp4"
    create_shorts_video(slides=yt["slides"], output_path=video_path)

    print("📤 YouTube 업로드 중...")
    yt_url = upload_youtube_short(
        video_path=video_path,
        title=yt["title"],
        description=yt["description"],
        tags=yt.get("tags", []),
    )
    print(f"   ✅ {yt_url}")

    # ── 3. 게시 완료 처리 ────────────────────────────────────
    content.update({"status": "published", "blog_url": blog_url, "youtube_url": yt_url})
    PUBLISHED_DIR.mkdir(exist_ok=True)
    published_path = PUBLISHED_DIR / f"{today}.json"
    published_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    if target != published_path:
        target.unlink()

    print(f"\n🎉 게시 완료!")
    print(f"   블로그 : {blog_url}")
    print(f"   YouTube : {yt_url}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("generate", "publish"):
        print("사용법: python daily_agent.py [generate|publish]")
        sys.exit(1)

    {"generate": cmd_generate, "publish": cmd_publish}[sys.argv[1]]()
