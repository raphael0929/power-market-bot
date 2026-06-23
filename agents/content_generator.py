"""템플릿 기반 블로그 글과 YouTube Shorts 스크립트 생성 (API 불필요)."""
import json
import os
import random
from datetime import date, datetime, timedelta
from pathlib import Path


# ── 주제 풀 ──────────────────────────────────────────────────────────────────
TOPICS = [
    "한국 전력시장 SMP 동향과 투자 인사이트",
    "재생에너지 확대가 전기요금에 미치는 영향",
    "전력 수요 피크와 공급 안정성 분석",
    "태양광·풍력 발전량이 SMP를 낮추는 이유",
    "한국 탈원전 정책과 전력시장 변화",
    "가스발전 vs 원자력: 전력시장 비용 비교",
    "전력시장 참여자가 알아야 할 SMP 결정 메커니즘",
    "계절별 전력 수요 패턴과 SMP 예측 방법",
]

# ── 블로그 템플릿 ─────────────────────────────────────────────────────────────
BLOG_TEMPLATES = [
    {
        "title_fmt": "{date} 전력시장 SMP 동향 분석 및 전망",
        "labels": ["전력시장", "SMP", "에너지", "한국전력"],
        "html_fmt": """<h2>📊 {date} 전력시장 현황</h2>
<p>오늘 한국 전력시장의 주요 지표를 분석합니다. 계통한계가격(SMP)과 전력 수요 동향을 살펴보고 향후 전망을 짚어봅니다.</p>

<h3>✅ 오늘의 핵심 포인트</h3>
<ul>
  <li><strong>SMP 동향</strong>: 최근 SMP는 연료비 변동과 재생에너지 출력에 따라 시간대별 변동폭이 확대되고 있습니다.</li>
  <li><strong>수요 현황</strong>: 계절적 요인으로 전력 수요가 {demand_trend}하는 추세를 보이고 있습니다.</li>
  <li><strong>재생에너지</strong>: 태양광 발전 비중 증가로 낮 시간대 SMP 하락 압력이 지속되고 있습니다.</li>
</ul>

<h3>📈 SMP 결정 요인 분석</h3>
<p>SMP(System Marginal Price)는 전력시장에서 마지막으로 투입되는 발전기의 변동비로 결정됩니다. 주요 결정 요인은 다음과 같습니다.</p>
<ul>
  <li>LNG 연료비 변동: 국제 LNG 가격이 국내 SMP에 직접적인 영향을 미칩니다.</li>
  <li>재생에너지 출력: 태양광·풍력 발전량 증가 시 SMP 하락 요인이 됩니다.</li>
  <li>전력 수요: 수요 증가 시 고비용 발전기 투입으로 SMP 상승합니다.</li>
  <li>원전 이용률: 원전 출력 변동에 따른 가스발전 의존도 변화가 SMP에 영향을 줍니다.</li>
</ul>

<h3>🔍 투자자 및 사업자를 위한 인사이트</h3>
<p>전력시장 참여자들은 SMP 변동성을 리스크로 관리하면서도 기회로 활용할 수 있습니다.</p>
<ul>
  <li>피크 시간대(저녁 18~21시) 고SMP 구간을 활용한 ESS 충방전 전략을 검토하세요.</li>
  <li>재생에너지 발전사업자는 REC 가격 동향과 함께 SMP를 종합적으로 분석해야 합니다.</li>
  <li>전력 다소비 기업은 DR(수요반응) 프로그램 참여로 비용을 절감할 수 있습니다.</li>
</ul>

<h3>📌 내일 전망</h3>
<p>{forecast}</p>

<p>매일 업데이트되는 전력시장 분석 리포트를 구독하시면 최신 정보를 빠르게 받아보실 수 있습니다. 아래 구독 버튼을 눌러주세요! 💡</p>""",
    },
    {
        "title_fmt": "{date} 재생에너지 발전 동향과 전력망 영향 분석",
        "labels": ["재생에너지", "태양광", "풍력", "전력시장"],
        "html_fmt": """<h2>🌱 {date} 재생에너지 발전 현황</h2>
<p>국내 재생에너지 발전량이 꾸준히 증가하면서 전력시장에 새로운 변화를 만들어내고 있습니다. 오늘은 태양광·풍력 발전 동향과 전력망에 미치는 영향을 분석합니다.</p>

<h3>✅ 오늘의 핵심 데이터</h3>
<ul>
  <li><strong>태양광 발전</strong>: 낮 시간대 태양광 출력 증가로 SMP 하락 현상이 뚜렷하게 나타납니다.</li>
  <li><strong>오리 곡선(Duck Curve)</strong>: 낮 시간대 수요 감소, 저녁 급등 패턴이 심화되고 있습니다.</li>
  <li><strong>출력 제한</strong>: 재생에너지 급증으로 계통 수용 한계에 따른 출력 제한 사례가 증가 중입니다.</li>
</ul>

<h3>📊 재생에너지가 SMP에 미치는 영향</h3>
<p>재생에너지의 변동성 발전 특성은 전력시장 운영에 새로운 도전을 제시합니다.</p>
<ul>
  <li>태양광 발전 피크(11~14시): SMP 최저점 형성</li>
  <li>태양광 발전 종료 후(18~21시): SMP 급등 구간</li>
  <li>흐린 날·우기: 재생에너지 급감으로 가스발전 의존도 상승 → SMP 상승</li>
</ul>

<h3>🔋 ESS와 DR의 역할</h3>
<p>재생에너지 변동성 대응을 위한 에너지저장장치(ESS)와 수요반응(DR)의 중요성이 커지고 있습니다.</p>
<ul>
  <li>ESS: 낮 시간대 충전 → 저녁 피크 방전으로 수익 창출</li>
  <li>DR: 피크 수요 감축 참여로 보조금 수취</li>
  <li>V2G(Vehicle-to-Grid): 전기차 배터리를 전력망 자원으로 활용하는 미래 솔루션</li>
</ul>

<h3>📌 시사점</h3>
<p>{forecast}</p>
<p>재생에너지 확대는 전력시장의 패러다임을 바꾸고 있습니다. 변화하는 시장에 선제적으로 대응하는 것이 중요합니다. 더 많은 인사이트를 원하시면 구독해주세요! 🌿</p>""",
    },
]

# ── YouTube Shorts 템플릿 ──────────────────────────────────────────────────────
YT_TEMPLATES = [
    {
        "title_fmt": "오늘 전기값 왜 올랐나? SMP 완전 해설 ({date})",
        "description_fmt": "📊 {date} 전력시장 SMP 동향\n재생에너지와 가스발전이 만들어내는 전기요금의 비밀\n#SMP #전력시장 #에너지",
        "tags": ["SMP", "전력시장", "전기요금", "에너지", "재생에너지"],
        "slides": [
            {"text": "전기요금 왜 오르나?", "narration": "여러분, 전기요금이 왜 오르는지 궁금하셨죠? 30초만 보시면 이해됩니다."},
            {"text": "SMP란?", "narration": "SMP는 계통한계가격으로, 전력시장에서 마지막으로 투입되는 발전기의 연료비가 기준이 됩니다."},
            {"text": "LNG가 핵심!", "narration": "대부분의 상황에서 가스발전기가 마지막 발전기가 되어 LNG 가격이 SMP를 결정합니다."},
            {"text": "재생에너지 효과", "narration": "태양광이 많이 발전하면 SMP가 낮아집니다. 그래서 낮 시간대 전기가 더 쌉니다."},
            {"text": "오늘의 인사이트", "narration": "전력시장을 이해하면 에너지 비용을 절감할 수 있습니다. 구독하고 매일 확인하세요!"},
        ],
    },
    {
        "title_fmt": "재생에너지가 늘수록 전기가 싸질까? ({date})",
        "description_fmt": "🌱 재생에너지 확대와 전력시장 변화\n태양광·풍력이 SMP에 미치는 진짜 영향\n#재생에너지 #태양광 #전력시장",
        "tags": ["재생에너지", "태양광", "풍력", "SMP", "에너지전환"],
        "slides": [
            {"text": "재생에너지 = 전기 저렴?", "narration": "재생에너지가 늘면 전기가 싸질까요? 정답은 '낮에는 YES, 저녁엔 NO'입니다."},
            {"text": "낮엔 SMP 하락", "narration": "태양광이 최대 출력일 때 SMP는 최저점을 기록합니다. 연료비가 0이니까요."},
            {"text": "저녁엔 SMP 급등", "narration": "해가 지면 태양광이 사라지고 가스발전기가 다시 투입되며 SMP가 급등합니다."},
            {"text": "오리 곡선 현상", "narration": "이것을 오리 곡선이라 부릅니다. 재생에너지가 많을수록 이 패턴이 심해집니다."},
            {"text": "ESS가 해답!", "narration": "에너지저장장치로 낮에 충전하고 저녁에 방전하면 이 문제를 해결할 수 있습니다. 구독해주세요!"},
        ],
    },
]


def generate_daily_content(topic: str | None = None) -> dict:
    """템플릿 기반으로 오늘의 콘텐츠 초안을 생성합니다 (API 불필요)."""
    today = date.today()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]

    # 주제 선정
    if not topic:
        idx = today.toordinal() % len(TOPICS)
        topic = TOPICS[idx]
    print(f"📌 주제: {topic}")

    # 수요 트렌드 (계절 기반)
    month = today.month
    if month in [6, 7, 8]:
        demand_trend = "증가"
        forecast = "무더위로 냉방 수요가 지속 증가할 전망입니다. SMP 상승 압력이 이어질 것으로 예상되며, 특히 오후 피크 시간대(14~17시) 수요 집중이 예상됩니다."
    elif month in [12, 1, 2]:
        demand_trend = "증가"
        forecast = "동절기 난방 수요 증가로 전력 수요가 높은 수준을 유지할 전망입니다. LNG 가격 동향과 함께 SMP 변동성에 주목하시기 바랍니다."
    elif month in [3, 4, 5]:
        demand_trend = "감소"
        forecast = "봄철 냉난방 수요 감소로 전력 수요가 연중 최저 수준을 기록할 전망입니다. 재생에너지 출력 증가와 맞물려 SMP 하락세가 예상됩니다."
    else:
        demand_trend = "안정"
        forecast = "가을철 적정 기온으로 냉난방 수요가 낮은 수준을 유지할 전망입니다. 계통 안정성이 양호하며 SMP도 안정적인 흐름이 예상됩니다."

    # 블로그 템플릿 선택
    blog_tmpl = BLOG_TEMPLATES[today.toordinal() % len(BLOG_TEMPLATES)]
    blog_title = blog_tmpl["title_fmt"].format(date=date_str)
    blog_html = blog_tmpl["html_fmt"].format(
        date=date_str,
        weekday=weekday,
        demand_trend=demand_trend,
        forecast=forecast,
        topic=topic,
    )

    # YouTube 템플릿 선택
    yt_tmpl = YT_TEMPLATES[today.toordinal() % len(YT_TEMPLATES)]
    yt_title = yt_tmpl["title_fmt"].format(date=date_str)
    yt_desc = yt_tmpl["description_fmt"].format(date=date_str)

    return {
        "date": today.isoformat(),
        "topic": topic,
        "blog": {
            "title": blog_title,
            "html_content": blog_html,
            "labels": blog_tmpl["labels"],
        },
        "youtube": {
            "title": yt_title,
            "description": yt_desc,
            "tags": yt_tmpl["tags"],
            "slides": yt_tmpl["slides"],
        },
        "status": "draft",
    }


if __name__ == "__main__":
    content = generate_daily_content()
    print(json.dumps(content, ensure_ascii=False, indent=2))
