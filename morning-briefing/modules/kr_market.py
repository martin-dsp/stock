"""전일 거래량 상위 / 급등락 종목 + 종목별 뉴스

데이터 소스:
  시세(거래량·등락률): FinanceDataReader (KRX 전일 종가 기준, 장 전도 정상 작동)
  종목별 뉴스:         네이버 금융 종목 뉴스 페이지 스크래핑
"""
import logging
import re
import time

import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
LIMIT = 10


def _load_market_data() -> pd.DataFrame:
    """KOSPI + KOSDAQ 전종목 전일 시세 로드"""
    df_k  = fdr.StockListing("KOSPI")
    df_kq = fdr.StockListing("KOSDAQ")
    df = pd.concat([df_k, df_kq], ignore_index=True)
    df = df[df["Volume"] > 0].copy()
    return df


def _fetch_stock_news(code: str, name: str, limit: int = 2) -> list[dict]:
    """네이버 종목 뉴스 최근 헤드라인 + 링크"""
    if not code:
        return []
    results = []
    try:
        url  = f"https://finance.naver.com/item/news_news.naver?code={code}&page=1"
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.select("table.type5 tr td.title a[href]"):
            title = a.get_text(strip=True)
            href  = a.get("href", "")
            if not title:
                continue
            if href.startswith("/"):
                href = "https://finance.naver.com" + href
            results.append({"title": title, "url": href})
            if len(results) >= limit:
                break
    except Exception as e:
        logging.error(f"종목 뉴스 [{name}] 오류: {e}")
    return results


def _to_item(row) -> dict:
    return {
        "code":       str(row["Code"]).zfill(6),
        "name":       row["Name"],
        "market":     row["Market"],
        "price":      int(row["Close"]),
        "change_pct": round(float(row["ChagesRatio"]), 2),
        "volume":     int(row["Volume"]),
        "news":       [],
    }


def _attach_news(items: list[dict]) -> None:
    for item in items:
        item["news"] = _fetch_stock_news(item["code"], item["name"])
        time.sleep(0.4)


def fetch():
    result = {"volume_top": [], "gainers": [], "losers": []}
    try:
        df = _load_market_data()

        # 거래량 상위
        result["volume_top"] = [
            _to_item(row)
            for _, row in df.nlargest(LIMIT, "Volume").iterrows()
        ]

        # 급등 상위
        result["gainers"] = [
            _to_item(row)
            for _, row in df.nlargest(LIMIT, "ChagesRatio").iterrows()
        ]
        _attach_news(result["gainers"])

        # 급락 상위
        result["losers"] = [
            _to_item(row)
            for _, row in df.nsmallest(LIMIT, "ChagesRatio").iterrows()
        ]
        _attach_news(result["losers"])

    except Exception as e:
        logging.error(f"kr_market 오류: {e}")
    return result
