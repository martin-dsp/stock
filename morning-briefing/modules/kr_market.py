"""전일 거래량 상위 / 급등락 종목 — 네이버 금융 스크래핑

NOTE: pykrx는 KRX API 응답 형식 변경으로 동작하지 않아 네이버 금융으로 대체.
      스크래핑 대상 URL:
        거래량 상위: https://finance.naver.com/sise/sise_quant.naver?sosok={0|1}
        급등:        https://finance.naver.com/sise/sise_rise.naver?sosok={0|1}
        급락:        https://finance.naver.com/sise/sise_fall.naver?sosok={0|1}
      HTML 구조 변경 시 파싱 실패 가능 — 에러 로그 확인 필요.
"""
import logging
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

# sosok: 0=KOSPI, 1=KOSDAQ
MARKETS = {"KOSPI": "0", "KOSDAQ": "1"}


def _parse_table(url: str, limit: int = 5) -> list[dict]:
    """네이버 시세 테이블 파싱 (공통).

    열 순서: 순위 | 종목명 | 현재가 | 전일대비 | 등락률 | 거래량 | ...
    """
    rows_data = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table.type_2 tr")

        for row in rows:
            cols = [td.get_text(strip=True) for td in row.select("td")]
            if len(cols) < 6:
                continue

            name       = cols[1]
            price_str  = cols[2].replace(",", "")
            change_str = cols[4].replace("%", "").replace("+", "")
            vol_str    = cols[5].replace(",", "")

            if not name or not price_str.isdigit():
                continue

            rows_data.append({
                "name":       name,
                "price":      int(price_str),
                "change_pct": float(change_str) if change_str else 0.0,
                "volume":     int(vol_str) if vol_str.isdigit() else 0,
            })

            if len(rows_data) >= limit:
                break
    except Exception as e:
        logging.error(f"kr_market 스크래핑 오류 ({url}): {e}")
    return rows_data


def fetch():
    result = {"volume_top": [], "gainers": [], "losers": []}

    try:
        # KOSPI + KOSDAQ 거래량 상위를 합쳐서 거래량 기준 재정렬
        vol_all = []
        for market, sosok in MARKETS.items():
            url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
            items = _parse_table(url, limit=10)
            for item in items:
                item["market"] = market
            vol_all.extend(items)
            time.sleep(0.3)

        vol_all.sort(key=lambda x: x["volume"], reverse=True)
        result["volume_top"] = vol_all[:5]

        # 급등 (KOSPI 기준, 장 상황에 따라 KOSDAQ 추가 가능)
        gainers = []
        for market, sosok in MARKETS.items():
            url = f"https://finance.naver.com/sise/sise_rise.naver?sosok={sosok}"
            items = _parse_table(url, limit=5)
            for item in items:
                item["market"] = market
            gainers.extend(items)
            time.sleep(0.3)

        gainers.sort(key=lambda x: x["change_pct"], reverse=True)
        result["gainers"] = gainers[:5]

        # 급락
        losers = []
        for market, sosok in MARKETS.items():
            url = f"https://finance.naver.com/sise/sise_fall.naver?sosok={sosok}"
            items = _parse_table(url, limit=5)
            for item in items:
                item["market"] = market
            losers.extend(items)
            time.sleep(0.3)

        losers.sort(key=lambda x: x["change_pct"])
        result["losers"] = losers[:5]

    except Exception as e:
        logging.error(f"kr_market 전체 오류: {e}")

    return result
