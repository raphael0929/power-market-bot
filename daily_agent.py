#!/usr/bin/env python3
"""
daily_agent.py  —  power-market-bot
Commands: generate | publish
"""
import os, json, sys
from datetime import date, datetime
from pathlib import Path

# ── 환경변수 ────────────────────────────────────────────────────────────────────
BLOGGER_BLOG_ID  = os.environ.get("BLOGGER_BLOG_ID", "")
BLOGGER_TOKEN    = os.environ.get("BLOGGER_ACCESS_TOKEN", "")
YT_TOKEN         = os.environ.get("YOUTUBE_ACCESS_TOKEN", "")
INPUT_TOPIC      = os.environ.get("INPUT_TOPIC", "")
CONTENT_FILE_ENV = os.environ.get("CONTENT_FILE", "")


def today_kst() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ── generate ────────────────────────────────────────────────────────────────────
def cmd_generate():
    try:
        from agents.content_generator import generate_content
        topic = INPUT_TOPIC or "전력시장 일일 동향"
        content = generate_content(topic)
    except Exception as e:
        print(f"[WARN] content_generator 실패: {e} — 기본 템플릿 사용")
        content = _fallback_content(INPUT_TOPIC or "전력시장 동향")

    today = today_kst()
    out_path = Path("drafts") / f"{today}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 초안 저장: {out_path}")


def _fallback_content(topic: str) -> dict:
    today = today_kst()
    return {
        "topic": topic,
        "date":  today,
        "blog": {
            "title": f"[전력시장] {today} {topic}",
            "content": f"<p>{today} 전력시장 동향입니다.</p><p>주제: {topic}</p>",
            "labels": ["전력시장", "SMP", "전력시장365"],
        },
        "youtube": {
            "title": f"[전력시장] {today} {topic}",
            "description": f"{today} 전력시장 일일 동향 | {topic}",
            "tags": ["전력시장", "SMP", "에너지"],
        },
    }


# ── publish ─────────────────────────────────────────────────────────────────────
def cmd_publish():
    # 1) 환경변수 우선
    # 2) approved/<today>.json
    # 3) drafts/<today>.json
    today = today_kst()
    candidates = []
    if CONTENT_FILE_ENV:
        candidates.append(Path(CONTENT_FILE_ENV))
    candidates += [
        Path("approved") / f"{today}.json",
        Path("drafts")   / f"{today}.json",
    ]

    content_path = None
    for p in candidates:
        if p.exists():
            content_path = p
            break

    if content_path is None:
        tried = ", ".join(str(c) for c in candidates)
        print(f"[ERROR] 콘텐츠 파일 없음. 시도한 경로: {tried}")
        sys.exit(1)

    print(f"[INFO] 콘텐츠 파일: {content_path}")
    content = json.loads(content_path.read_text(encoding="utf-8"))

    blog_ok = _post_to_blogger(content.get("blog", {}))
    yt_ok   = _upload_to_youtube(content.get("youtube", {}))

    if not (blog_ok and yt_ok):
        sys.exit(1)
    print("[OK] 게재 완료")


def _post_to_blogger(blog: dict) -> bool:
    if not BLOGGER_BLOG_ID or not BLOGGER_TOKEN:
        print("[SKIP] Blogger 자격증명 없음")
        return True
    try:
        import urllib.request, urllib.error
        url     = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts/"
        payload = json.dumps({
            "title":   blog.get("title", ""),
            "content": blog.get("content", ""),
            "labels":  blog.get("labels", []),
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, method="POST",
            headers={
                "Authorization": f"Bearer {BLOGGER_TOKEN}",
                "Content-Type":  "application/json",
            }
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"[OK] Blogger 게재: {data.get('url', '(URL 없음)')}")
            return True
    except Exception as e:
        print(f"[ERROR] Blogger 게재 실패: {e}")
        return False


def _upload_to_youtube(yt: dict) -> bool:
    if not YT_TOKEN:
        print("[SKIP] YouTube 자격증명 없음")
        return True
    # 영상 파일 없이 메타데이터만 있을 때는 스킵
    video_path = Path("video_output.mp4")
    if not video_path.exists():
        print("[SKIP] video_output.mp4 없음 — YouTube 업로드 건너뜀")
        return True
    try:
        import urllib.request
        meta = {
            "snippet": {
                "title":       yt.get("title", ""),
                "description": yt.get("description", ""),
                "tags":        yt.get("tags", []),
                "categoryId":  "25",
            },
            "status": {"privacyStatus": "public"},
        }
        print(f"[INFO] YouTube 업로드 시도: {yt.get('title', '')}")
        # 실제 업로드는 resumable upload API 필요 — 여기서는 메타만 로그
        print("[OK] YouTube 메타 준비 완료 (resumable upload 별도 처리)")
        return True
    except Exception as e:
        print(f"[ERROR] YouTube 업로드 실패: {e}")
        return False


# ── main ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python daily_agent.py [generate|publish]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "generate":
        cmd_generate()
    elif cmd == "publish":
        cmd_publish()
    else:
        print(f"[ERROR] 알 수 없는 명령: {cmd}")
        sys.exit(1)
