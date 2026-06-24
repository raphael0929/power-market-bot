name: Generate Naver Blog Drafts

on:
  schedule:
    - cron: '0 21 * * *'   # 매일 KST 06:00 (UTC 21:00 전날)
  workflow_dispatch:
    inputs:
      target_date:
        description: '날짜 (YYYY-MM-DD, 기본값: 오늘 KST)'
        required: false

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Determine KST date
        id: date
        run: |
          if [ -n "${{ github.event.inputs.target_date }}" ]; then
            echo "TARGET=${{ github.event.inputs.target_date }}" >> $GITHUB_OUTPUT
          else
            echo "TARGET=$(TZ='Asia/Seoul' date +'%Y-%m-%d')" >> $GITHUB_OUTPUT
          fi

      - name: Generate HTML drafts
        run: |
          mkdir -p naver-drafts
          python agents/naver_content_generator.py ${{ steps.date.outputs.TARGET }} naver-drafts

      - name: Commit and push drafts
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add naver-drafts/
          git diff --cached --quiet || git commit -m "📝 네이버 블로그 초안 ${{ steps.date.outputs.TARGET }}"
          git push
