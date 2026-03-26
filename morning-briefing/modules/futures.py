"""선물/지수

- S&P500·나스닥100 선물 (ES=F, NQ=F): 1분봉으로 현재 실시간 가격
- KOSPI·KOSDAQ: 네이버 모바일 API (8시 기준 전일 종가)
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
    "KOSPI":  "KOSPI",
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
    """1분봉으로 현재 실시간 선물 가격 조회"""
    result = {}
    for name, ticker in US_FUTURES.items():
        try:
            t = yf.Ticker(ticker)
            # 현재가: 1분봉
            hist_1m = t.history(period="1d", interval="1m")
            # 전일 종가: 변동률 계산용
            hist_1d = t.history(period="2d")

            if hist_1m.empty:
                raise ValueError(f"{ticker} 1분봉 데이터 없음")

            curr = float(hist_1m["Close"].iloc[-1])

            if len(hist_1d) >= 2:
                prev = float(hist_1d["Close"].iloc[-2])
            else:
                prev = curr

            change_pct = (curr - prev) / prev * 100
            result[name] = {"price": curr, "change_pct": change_pct, "realtime": True}
            time.sleep(0.3)
        except Exception as e:
            logging.error(f"futures {name} 오류: {e}")
    return result


def _fetch_kr_indices():
    """네이버 모바일 API로 KOSPI/KOSDAQ 지수 조회 (전일 종가)"""
    result = {}
    for name, code in KR_INDICES.items():
        try:
            url  = f"https://m.stock.naver.com/api/index/{code}/basic"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            price = data.get("closePrice", "N/A")
            ratio = data.get("fluctuationsRatio")

            result[name] = {
                "price":      price,
                "change_pct": float(ratio) if ratio else None,
                "realtime":   False,
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
