"""미국 3대 지수 (전일 종가) + USD/KRW 환율 (현재 실시간)

- 지수(^GSPC, ^IXIC, ^DJI): 8시 KST 기준 이미 마감 → 전일 종가 사용
- USD/KRW(KRW=X): 외환은 24시간 거래 → 현재 환율 실시간 사용
"""
import time
import logging
import yfinance as yf

INDEX_TICKERS = {
    "S&P500":    "^GSPC",
    "Nasdaq":    "^IXIC",
    "Dow Jones": "^DJI",
}


def _fetch_indices():
    result = {}
    for name, ticker in INDEX_TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 2:
                prev  = hist["Close"].iloc[-2]
                curr  = hist["Close"].iloc[-1]
            elif len(hist) == 1:
                curr = hist["Close"].iloc[0]
                prev = curr
            else:
                result[name] = None
                continue

            change     = curr - prev
            change_pct = change / prev * 100
            result[name] = {
                "price":      float(curr),
                "change":     float(change),
                "change_pct": float(change_pct),
                "realtime":   False,
            }
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"us_markets {name} 오류: {e}")
            result[name] = None
    return result


def _fetch_usdkrw():
    """USD/KRW 현재 환율 (1분봉 실시간)"""
    try:
        ticker = yf.Ticker("KRW=X")
        # 현재가: 1분봉으로 오늘 데이터
        hist_1m = ticker.history(period="1d", interval="1m")
        # 전일 종가: 등락 비교용
        hist_1d = ticker.history(period="2d")

        if hist_1m.empty:
            raise ValueError("KRW=X 1분봉 데이터 없음")

        curr = float(hist_1m["Close"].iloc[-1])

        if len(hist_1d) >= 2:
            prev = float(hist_1d["Close"].iloc[-2])
        else:
            prev = curr

        change     = curr - prev
        change_pct = change / prev * 100

        return {
            "price":      curr,
            "change":     change,
            "change_pct": change_pct,
            "realtime":   True,
        }
    except Exception as e:
        logging.error(f"us_markets USD/KRW 오류: {e}")
        return None


def fetch():
    result = _fetch_indices()
    result["USD/KRW"] = _fetch_usdkrw()
    return result
