"""뉴스 수집 + 번역

국내: 네이버 금융 스크래핑 (링크 포함, 10개)
해외: RSS 다중 소스 (Reuters, CNBC, Yahoo Finance) + 한국어 번역 + 중복 제거 (10개)
"""
import logging
import time

import feedparser
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

OVERSEAS_RSS = [
    ("Reuters",       "https://feeds.reuters.com/reuters/businessNews"),
    ("CNBC",          "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("Yahoo Finance", "https://finance.yahoo.com/rss/topstories"),
]

STOP_WORDS = {
    "the", "a", "an", "is", "are", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "says", "after", "as", "its", "it",
    "by", "with", "from", "that", "this", "be", "has", "have", "had",
}


def _translate(text: str) -> str:
    """영어 → 한국어 번역 (Google Translate, deep-translator)"""
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target="ko").translate(text[:500])
    except Exception as e:
        logging.warning(f"번역 실패: {e}")
        return text


def _is_duplicate(title: str, seen: list[str], threshold: int = 4) -> bool:
    """핵심 단어 겹침으로 유사 기사 판별"""
    words_new = set(title.lower().split()) - STOP_WORDS
    for seen_title in seen:
        words_ex = set(seen_title.lower().split()) - STOP_WORDS
        if len(words_new & words_ex) >= threshold:
            return True
    return False


def _fetch_naver_news(limit: int = 10) -> list[dict]:
    """네이버 금융 주요 뉴스 스크래핑 (링크 포함)"""
    news_list = []
    urls_to_try = [
        "https://finance.naver.com/news/mainnews.naver",
        "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258",
    ]

    for page_url in urls_to_try:
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # 여러 셀렉터 시도
            anchors = (
                soup.select(".mainNewsList li a[href]")
                or soup.select(".newsList li a[href]")
                or soup.select(".articleSubject a[href]")
                or soup.select("ul.newsList a[href]")
            )

            seen_titles = []
            for a in anchors:
                title = a.get_text(strip=True)
                href  = a.get("href", "")
                if not title or len(title) < 5:
                    continue
                if title in seen_titles:
                    continue
                seen_titles.append(title)

                if href.startswith("/"):
                    href = "https://finance.naver.com" + href
                elif not href.startswith("http"):
                    continue

                news_list.append({"title": title, "url": href})
                if len(news_list) >= limit:
                    break

        except Exception as e:
            logging.error(f"네이버 뉴스 스크래핑 오류 ({page_url}): {e}")

        if len(news_list) >= limit:
            break

    return news_list[:limit]


def _fetch_rss(feed_url: str, source: str, limit: int = 15) -> list[dict]:
    news_list = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            title = entry.get("title", "").strip()
            url   = entry.get("link", "")
            if title:
                news_list.append({"title": title, "url": url, "source": source})
    except Exception as e:
        logging.error(f"{source} RSS 오류: {e}")
    return news_list


def fetch():
    result = {"domestic": [], "international": []}

    # 국내 뉴스
    result["domestic"] = _fetch_naver_news(limit=10)

    # 해외 뉴스: 다중 소스 수집 → 중복 제거 → 번역
    raw = []
    for source, rss_url in OVERSEAS_RSS:
        items = _fetch_rss(rss_url, source, limit=15)
        raw.extend(items)
        time.sleep(0.3)

    # 중복 제거 (원문 제목 기준)
    seen_titles = []
    deduped = []
    for item in raw:
        if not _is_duplicate(item["title"], seen_titles):
            seen_titles.append(item["title"])
            deduped.append(item)
        if len(deduped) >= 10:
            break

    # 번역
    for item in deduped:
        item["title_ko"] = _translate(item["title"])
        time.sleep(0.2)

    result["international"] = deduped

    return result
