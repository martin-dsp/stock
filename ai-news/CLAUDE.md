# CLAUDE.md — AI 뉴스

## 개요

AI 관련 최신 뉴스를 RSS 피드에서 수집해 매일 오전 8시 슬랙으로 발송.
클로드/Anthropic 뉴스 포함.

## 기술 스택

- Python 3.10+
- 데이터 수집: feedparser (RSS), deep-translator (번역)
- 메시지 발송: Slack Incoming Webhook
- 스케줄링: GitHub Actions + 맥미니 셀프호스티드 러너 (매일 오전 8시)

## RSS 소스

- Anthropic Blog: https://www.anthropic.com/rss.xml
- OpenAI Blog: https://openai.com/blog/rss.xml
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/feed/
- The Verge AI: https://www.theverge.com/rss/ai-artificial-intelligence/index.xml
- MIT Tech Review: https://www.technologyreview.com/topic/artificial-intelligence/feed

## 환경 변수 (.env)

- `SLACK_WEBHOOK_URL` — 슬랙 Incoming Webhook URL (ai-뉴스 채널)

## 모듈 구조

- `ai_feeds.py` — 5개 RSS 소스 수집 + 중복 제거 + 번역
- `rss_fetcher.py` — RSS 파싱 + 중복 제거 유틸
- `translator.py` — deep-translator 래퍼
- `slack_sender.py` — 슬랙 메시지 포맷팅 + 발송

## 주의사항

- RSS 피드 URL은 사이트 정책에 따라 변경될 수 있음
- deep-translator는 Google Translate 비공식 API — 간헐적 실패 가능 (원문 fallback 처리됨)
