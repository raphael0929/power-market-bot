"""Claude API로 블로그 글과 YouTube Shorts 스크립트를 생성합니다."""
import json
import os
import re
from datetime import date

import anthropic


def _parse_json_response(text: str) -> dict:
    """LLM 응답에서 JSON 블록을 파싱합니다."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def generate_daily_content(topic: str | None = None) -> dict:
    """오늘의 콘텐츠 초안(블로그 + YouTube Shorts)을 생성합니다."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = date.today().strftime("%Y년 %m월 %d일")

    # 주제 자동 선정
    if not topic:
        resp = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"오늘({today}) 한국 독자에게 유익한 블로그·YouTube 주제를 하나 추천해주세요.\n"
                    "AI, 기술, 자기계발, 비즈니스 중 하나로 선택합니다.\n"
                    "제목만 출력하세요. 부연설명 없이."
                )
            }]
        )
        topic = resp.content[0].text.strip()

    print(f"  주제: {topic}")

    # 블로그 글 생성
    blog_resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""주제: {topic}

Google Blogspot용 한국어 블로그 글을 작성해주세요.

조건:
- HTML 형식 (h2, h3, p, ul, li 태그 사용)
- 분량: 1000~1500자
- 독자가 실제로 활용할 수 있는 실용적 내용
- 자연스럽고 친근한 말투

아래 JSON 형식으로만 출력 (마크다운 코드블록 감싸도 됨):
{{"title": "제목", "html_content": "HTML 본문", "labels": ["태그1", "태그2", "태그3"]}}"""
        }]
    )
    blog_data = _parse_json_response(blog_resp.content[0].text)

    # YouTube Shorts 스크립트 생성
    yt_resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""주제: {topic}

60초 YouTube Shorts 영상 스크립트를 작성해주세요.

조건:
- 슬라이드 5장 (각 ~12초)
- 슬라이드 1: 강렬한 후크 (질문 or 충격 발언)
- 슬라이드 2~4: 핵심 내용 (각 1포인트)
- 슬라이드 5: 정리 + 구독 유도 CTA
- text: 화면에 보여줄 짧은 텍스트 (15자 이내)
- narration: TTS로 읽을 나레이션 (한 문장)

아래 JSON 형식으로만 출력 (마크다운 코드블록 감싸도 됨):
{{"title": "영상 제목 (검색 최적화)", "description": "영상 설명 (3줄 이내)", "tags": ["태그1", "태그2", "태그3"], "slides": [{{"text": "화면 텍스트", "narration": "나레이션 텍스트"}}]}}"""
        }]
    )
    yt_data = _parse_json_response(yt_resp.content[0].text)

    return {
        "date": date.today().isoformat(),
        "topic": topic,
        "blog": blog_data,
        "youtube": yt_data,
        "status": "draft",
    }
