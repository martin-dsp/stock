# CLAUDE.md — 세계 뉴스

## 개요

세계 주요 뉴스를 RSS 피드에서 수집해 매일 오전 8시 슬랙으로 발송.

## 기술 스택

- Python 3.10+
- 데이터 수집: feedparser (RSS), deep-translator (번역)
- 메시지 발송: Slack Incoming Webhook
- 스케줄링: GitHub Actions + 맥미니 셀프호스티드 러너 (매일 오전 8시)

## RSS 소스

- BBC World: http://feeds.bbci.co.uk/news/world/rss.xml
- The Guardian: https://www.theguardian.com/world/rss
- Al Jazeera: https://www.aljazeera.com/xml/rss/all.xml
- NPR: https://feeds.npr.org/1001/rss.xml

## 환경 변수 (.env)

- `SLACK_WEBHOOK_URL` — 슬랙 Incoming Webhook URL (세계-뉴스 채널)

## 모듈 구조

- `world_feeds.py` — 4개 RSS 소스 수집 + 중복 제거 + 번역
- `rss_fetcher.py` — RSS 파싱 + 중복 제거 유틸
- `translator.py` — deep-translator 래퍼
- `slack_sender.py` — 슬랙 메시지 포맷팅 + 발송

## 주의사항

- RSS 피드 URL은 사이트 정책에 따라 변경될 수 있음
- deep-translator는 Google Translate 비공식 API — 간헐적 실패 가능 (원문 fallback 처리됨)
