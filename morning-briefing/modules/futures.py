"""야간선물: S&P500·나스닥100 (yfinance) + KOSPI·KOSDAQ 실시간 지수 (네이버 모바일 API)

NOTE: 네이버 금융의 야간선물 전용 페이지(/futr/) URL이 폐지됨.
      KOSPI200/KOSDAQ150 야간선물 대신 KOSPI/KOSDAQ 현재 지수를 표시.
"""
import time
import logging
import requests
import yfinance as yf

US_FUTURES = {
    "S&P500 선물":   "ES=F",
    "나스닥100 선물": "NQ=F",
}

KR_INDICES = {
    "KOSPI": "KOSPI",
    "KOSDAQ": "KOSDAQ",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _fetch_us_futures():
    result = {}
    for name, ticker in US_FUTURES.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 2:
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                change_pct = (curr - prev) / prev * 100
            elif len(hist) == 1:
                curr = hist["Close"].iloc[0]
                change_pct = 0.0
            else:
                continue
            result[name] = {"price": float(curr), "change_pct": float(change_pct)}
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"futures {name} 오류: {e}")
    return result


def _fetch_kr_indices():
    """네이버 모바일 API로 KOSPI/KOSDAQ 실시간 지수 조회"""
    result = {}
    for name, code in KR_INDICES.items():
        try:
            url = f"https://m.stock.naver.com/api/index/{code}/basic"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            price = data.get("closePrice", "N/A")
            ratio = data.get("fluctuationsRatio")

            result[name] = {
                "price":      price,
                "change_pct": float(ratio) if ratio else None,
            }
            time.sleep(0.3)
        except Exception as e:
            logging.error(f"futures {name} 네이버 API 오류: {e}")
    return result


def fetch():
    result = {}
    result.update(_fetch_kr_indices())
    result.update(_fetch_us_futures())
    return result
