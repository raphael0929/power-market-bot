"""
텍스트 슬라이드 + 한국어 TTS로 YouTube Shorts 영상(1080×1920, ~60초)을 생성합니다.

시스템 의존성: ffmpeg, fonts-nanum (Ubuntu)
  sudo apt-get install -y ffmpeg fonts-nanum
"""
import os
import textwrap
import tempfile
from pathlib import Path

from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
BG_COLOR = (10, 12, 30)
TEXT_COLOR = (240, 240, 255)
ACCENT = (255, 60, 60)
SUB_COLOR = (160, 160, 200)

NANUM_BOLD = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
NANUM_REG = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _draw_slide(slide_text: str, slide_idx: int, total: int, tmp_dir: str) -> str:
    """슬라이드 이미지를 생성하고 경로를 반환합니다."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 상단 진행 바
    bar_w = int(WIDTH * (slide_idx / total))
    draw.rectangle([0, 0, bar_w, 12], fill=ACCENT)

    # 슬라이드 번호 텍스트
    font_num = _load_font(NANUM_REG, 44)
    draw.text((48, 36), f"{slide_idx} / {total}", font=font_num, fill=SUB_COLOR)

    # 메인 텍스트 — 줄바꿈 후 중앙 배치
    font_main = _load_font(NANUM_BOLD, 96)
    lines = textwrap.wrap(slide_text, width=9)  # 9자 기준 줄바꿈
    wrapped = "\n".join(lines)

    bbox = draw.textbbox((0, 0), wrapped, font=font_main, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (WIDTH - tw) // 2, (HEIGHT - th) // 2
    draw.text((x, y), wrapped, font=font_main, fill=TEXT_COLOR, align="center")

    # 하단 구독 유도 (마지막 슬라이드)
    if slide_idx == total:
        font_cta = _load_font(NANUM_REG, 50)
        cta = "👍 좋아요 & 구독 부탁드려요!"
        draw.text((WIDTH // 2, HEIGHT - 180), cta, font=font_cta, fill=ACCENT, anchor="mm")

    path = os.path.join(tmp_dir, f"slide_{slide_idx:02d}.png")
    img.save(path, "PNG")
    return path


def create_shorts_video(slides: list, output_path: str) -> str:
    """슬라이드 목록으로 YouTube Shorts MP4를 생성하고 경로를 반환합니다."""
    with tempfile.TemporaryDirectory() as tmp:
        clips = []
        total = len(slides)

        for i, slide in enumerate(slides, 1):
            # 슬라이드 이미지
            img_path = _draw_slide(slide["text"], i, total, tmp)

            # 한국어 TTS 생성
            audio_path = os.path.join(tmp, f"audio_{i:02d}.mp3")
            gTTS(text=slide["narration"], lang="ko", slow=False).save(audio_path)

            audio = AudioFileClip(audio_path)
            duration = audio.duration + 0.8  # 슬라이드당 여백

            clip = (
                ImageClip(img_path)
                .set_duration(duration)
                .set_audio(audio)
            )
            clips.append(clip)

        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(tmp, "_temp_audio.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None,
        )
    return output_path
