"""전일 거래량 상위 / 급등락 종목 + 종목별 뉴스 + DART 공시 매칭

URL:
  거래량 상위: https://finance.naver.com/sise/sise_quant.naver?sosok={0|1}
  급등:        https://finance.naver.com/sise/sise_rise.naver?sosok={0|1}
  급락:        https://finance.naver.com/sise/sise_fall.naver?sosok={0|1}
  종목 뉴스:   https://finance.naver.com/item/news_news.naver?code={code}
"""
import logging
import re
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MARKETS = {"KOSPI": "0", "KOSDAQ": "1"}
LIMIT   = 10


def _parse_table(url: str, limit: int = LIMIT) -> list[dict]:
    """네이버 시세 테이블 파싱. 종목코드도 함께 추출.

    열 순서: 순위 | 종목명 | 현재가 | 전일대비 | 등락률 | 거래량 | ...
    """
    rows_data = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        for row in soup.select("table.type_2 tr"):
            tds = row.select("td")
            if len(tds) < 6:
                continue

            # 종목명 + 코드
            name_tag = tds[1].select_one("a[href]")
            if not name_tag:
                continue
            name = name_tag.get_text(strip=True)
            href = name_tag.get("href", "")
            m    = re.search(r"code=(\w+)", href)
            code = m.group(1) if m else ""

            # 가격 / 등락률 / 거래량
            cols       = [td.get_text(strip=True) for td in tds]
            price_str  = cols[2].replace(",", "")
            change_str = cols[4].replace("%", "").replace("+", "")
            vol_str    = cols[5].replace(",", "")

            if not price_str.isdigit():
                continue

            rows_data.append({
                "code":       code,
                "name":       name,
                "price":      int(price_str),
                "change_pct": float(change_str) if change_str else 0.0,
                "volume":     int(vol_str) if vol_str.isdigit() else 0,
                "news":       [],   # 나중에 채움
            })

            if len(rows_data) >= limit:
                break

    except Exception as e:
        logging.error(f"kr_market 스크래핑 오류 ({url}): {e}")
    return rows_data


def _fetch_stock_news(code: str, name: str, limit: int = 2) -> list[dict]:
    """네이버 종목 뉴스에서 최근 헤드라인 + 링크 가져오기"""
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


def _attach_news(items: list[dict]) -> None:
    """각 종목에 뉴스 2개씩 추가 (in-place)"""
    for item in items:
        item["news"] = _fetch_stock_news(item["code"], item["name"])
        time.sleep(0.4)


def fetch():
    result = {"volume_top": [], "gainers": [], "losers": []}

    try:
        # 거래량 상위
        vol_all = []
        for market, sosok in MARKETS.items():
            url   = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
            items = _parse_table(url, limit=LIMIT)
            for item in items:
                item["market"] = market
            vol_all.extend(items)
            time.sleep(0.3)

        vol_all.sort(key=lambda x: x["volume"], reverse=True)
        result["volume_top"] = vol_all[:LIMIT]

        # 급등
        gainers = []
        for market, sosok in MARKETS.items():
            url   = f"https://finance.naver.com/sise/sise_rise.naver?sosok={sosok}"
            items = _parse_table(url, limit=LIMIT)
            for item in items:
                item["market"] = market
            gainers.extend(items)
            time.sleep(0.3)

        gainers.sort(key=lambda x: x["change_pct"], reverse=True)
        result["gainers"] = gainers[:LIMIT]
        _attach_news(result["gainers"])

        # 급락
        losers = []
        for market, sosok in MARKETS.items():
            url   = f"https://finance.naver.com/sise/sise_fall.naver?sosok={sosok}"
            items = _parse_table(url, limit=LIMIT)
            for item in items:
                item["market"] = market
            losers.extend(items)
            time.sleep(0.3)

        losers.sort(key=lambda x: x["change_pct"])
        result["losers"] = losers[:LIMIT]
        _attach_news(result["losers"])

    except Exception as e:
        logging.error(f"kr_market 전체 오류: {e}")

    return result
