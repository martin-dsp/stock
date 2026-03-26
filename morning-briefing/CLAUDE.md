# CLAUDE.md — Morning Briefing

## 개요

한국 주식시장 개장 전(오전 8시) 단타 매매에 필요한 정보를 자동 수집해서 슬랙으로 발송하는 시스템.

## 기술 스택

- Python 3.10+
- 데이터 수집: yfinance, pykrx, BeautifulSoup, OpenDartReader
- 메시지 발송: Slack Incoming Webhook
- 스케줄링: macOS crontab (평일 오전 8시)

## 수집 항목

- 미국 3대 지수 마감 (S&P500, Nasdaq, Dow) — yfinance
- USD/KRW 환율 — yfinance
- 야간선물: KOSPI200, 코스닥150 (네이버 스크래핑), S&P500, 나스닥100 (yfinance)
- 전일 거래량 상위 / 급등락 종목 — pykrx + 네이버 스크래핑
- 국내 뉴스 (네이버 금융) + 해외 뉴스 (블룸버그, 로이터, CNBC) — 스크래핑
- 주요 공시 — DART API (OpenDartReader)

## 환경 변수 (.env)

- `SLACK_WEBHOOK_URL` — 슬랙 Incoming Webhook URL
- `DART_API_KEY` — DART OpenAPI 키 (https://opendart.fss.or.kr/ 에서 무료 발급)

## 모듈 구조

각 모듈은 독립적으로 동작해야 함. 하나가 실패해도 나머지 정보는 정상 발송.

- `us_markets.py` — 미국 지수 + 환율
- `futures.py` — 야간선물 4종
- `kr_market.py` — 거래량 상위, 급등락
- `news.py` — 국내 + 해외 뉴스
- `disclosures.py` — DART 공시
- `slack_sender.py` — 슬랙 메시지 포맷팅 + 발송

## 주의사항

- 스크래핑 대상 사이트(네이버 금융 등)의 HTML 구조가 바뀌면 파싱이 깨질 수 있음 — 에러 로그 확인 필요
- yfinance는 비공식 API라 가끔 차단될 수 있음 — 요청 간 sleep 넣을 것
- pykrx도 과도한 요청 시 KRX에서 차단 가능
- 모든 API는 무료
