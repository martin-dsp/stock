# CLAUDE.md — 테크 뉴스

## 개요

HackerNews 인기 글과 테크 미디어 RSS를 수집해 매일 오전 8시 슬랙으로 발송.

## 기술 스택

- Python 3.10+
- 데이터 수집: HN Algolia API, feedparser (RSS), deep-translator (번역)
- 메시지 발송: Slack Incoming Webhook
- 스케줄링: GitHub Actions + 맥미니 셀프호스티드 러너 (매일 오전 8시)

## 데이터 소스

- HackerNews: https://hn.algolia.com/api/v1/search?tags=front_page (포인트순 15개)
- TechCrunch: https://techcrunch.com/feed/
- Ars Technica: https://feeds.arstechnica.com/arstechnica/index

## 환경 변수 (.env)

- `SLACK_WEBHOOK_URL` — 슬랙 Incoming Webhook URL (테크-뉴스 채널)

## 모듈 구조

- `hackernews.py` — HN Algolia API 수집 + 포인트/댓글 정보 + 번역
- `tech_feeds.py` — RSS 2개 수집 + 중복 제거 + 번역
- `rss_fetcher.py` — RSS 파싱 + 중복 제거 유틸
- `translator.py` — deep-translator 래퍼
- `slack_sender.py` — 슬랙 메시지 포맷팅 + 발송 (HN + 테크미디어 2섹션)

## 주의사항

- HN Algolia API는 무료, API 키 불필요
- RSS 피드 URL은 사이트 정책에 따라 변경될 수 있음
- deep-translator는 Google Translate 비공식 API — 간헐적 실패 가능 (원문 fallback 처리됨)
