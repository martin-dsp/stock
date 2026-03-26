"""국내(네이버 금융) + 해외(Reuters·CNBC RSS) 뉴스"""
import logging
import requests
import feedparser
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

OVERSEAS_RSS = [
    ("Reuters",  "https://feeds.reuters.com/reuters/businessNews"),
    ("CNBC",     "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
]


def _fetch_naver_news(limit: int = 5) -> list[dict]:
    """네이버 금융 주요 뉴스 스크래핑.

    주의: HTML 구조 변경 시 파싱 실패. 에러 로그 확인 필요.
    """
    news_list = []
    try:
        url = "https://finance.naver.com/news/mainnews.naver"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 셀렉터 우선순위: 최신 → 구버전 대비
        items = (
            soup.select(".mainNewsList li a")
            or soup.select(".newsList li a")
            or soup.select(".articleSubject a")
        )
        for a in items[:limit]:
            title = a.get_text(strip=True)
            href  = a.get("href", "")
            if title:
                news_list.append({
                    "title": title,
                    "url":   "https://finance.naver.com" + href if href.startswith("/") else href,
                })
    except Exception as e:
        logging.error(f"네이버 뉴스 스크래핑 오류: {e}")
    return news_list


def _fetch_rss(feed_url: str, source: str, limit: int = 5) -> list[dict]:
    news_list = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            news_list.append({
                "title":  entry.get("title", ""),
                "url":    entry.get("link", ""),
                "source": source,
            })
    except Exception as e:
        logging.error(f"{source} RSS 오류: {e}")
    return news_list


def fetch():
    result = {"domestic": [], "international": []}

    result["domestic"] = _fetch_naver_news()

    overseas = []
    for source, rss_url in OVERSEAS_RSS:
        overseas.extend(_fetch_rss(rss_url, source))
    result["international"] = overseas[:5]

    return result
