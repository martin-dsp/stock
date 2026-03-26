"""미국 3대 지수 + USD/KRW 환율 (yfinance)"""
import time
import logging
import yfinance as yf

TICKERS = {
    "S&P500":    "^GSPC",
    "Nasdaq":    "^IXIC",
    "Dow Jones": "^DJI",
    "USD/KRW":   "KRW=X",
}


def fetch():
    result = {}
    for name, ticker in TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 2:
                prev  = hist["Close"].iloc[-2]
                curr  = hist["Close"].iloc[-1]
                change = curr - prev
                change_pct = change / prev * 100
            elif len(hist) == 1:
                curr = hist["Close"].iloc[0]
                change, change_pct = 0.0, 0.0
            else:
                result[name] = None
                continue

            result[name] = {
                "price":      float(curr),
                "change":     float(change),
                "change_pct": float(change_pct),
            }
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"us_markets {name} 오류: {e}")
            result[name] = None

    return result
