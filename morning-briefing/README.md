# Morning Briefing

매일 오전 8시, 한국 주식시장 개장 전 필요한 정보를 자동 수집해서 슬랙으로 발송

## 수집 항목

### 미국 증시 마감
- S&P500, Nasdaq, Dow Jones 종가 및 등락률

### 환율
- USD/KRW 환율 및 등락

### 야간선물
- KOSPI200, 코스닥150 (네이버 금융)
- S&P500 선물, 나스닥100 선물 (yfinance)

### 종목 정보
- 전일 거래량 상위 5종목
- 전일 급등/급락 상위 5종목

### 뉴스
- 국내: 네이버 금융 주요 뉴스 5건
- 해외: 블룸버그, 로이터, CNBC 헤드라인 5건

### 공시
- DART API 주요 공시 5건

## 구조

```
morning-briefing/
├── .venv/               # 가상환경 (gitignore 대상)
├── main.py              # 진입점
├── config.py            # 환경변수, 상수
├── .env                 # 시크릿 (SLACK_WEBHOOK_URL, DART_API_KEY)
├── requirements.txt
├── modules/
│   ├── us_markets.py    # 미국 지수 + 환율 (yfinance)
│   ├── futures.py       # 야간선물 (네이버 + yfinance)
│   ├── kr_market.py     # 거래량 상위, 급등락 (pykrx + 네이버)
│   ├── news.py          # 국내 + 해외 뉴스
│   ├── disclosures.py   # 공시 (DART API)
│   └── slack_sender.py  # 슬랙 포맷팅 + 발송
└── logs/
```

## Tech Stack

- **Python 3.10+**
- **yfinance** — 미국 지수, 환율, 미국 선물
- **pykrx** — 한국 시장 데이터
- **BeautifulSoup** — 네이버 금융 / 해외 뉴스 스크래핑
- **OpenDartReader** — DART 공시 API
- **Slack Incoming Webhook** — 메시지 발송

## 설정

### 1. 가상환경 생성 + 의존성 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
cp .env.example .env
# .env 파일에 아래 값 입력
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
# DART_API_KEY=...
```

### 3. 수동 실행 (테스트)
```bash
python main.py
```

### 4. 크론 등록 (평일 오전 8시)
```bash
crontab -e
# 아래 줄 추가
0 8 * * 1-5 cd ~/Desktop/stock/morning-briefing && .venv/bin/python main.py >> logs/briefing.log 2>&1
```

## API 키 발급 (전부 무료)

| API | 발급처 | 비용 |
|-----|--------|------|
| DART OpenAPI | https://opendart.fss.or.kr/ | 무료 |
| Slack Webhook | https://api.slack.com/messaging/webhooks | 무료 |
| yfinance | 키 필요 없음 | 무료 |
| pykrx | 키 필요 없음 | 무료 |
