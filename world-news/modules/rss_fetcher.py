"""RSS 피드 파싱 + 중복 제거"""
import logging
import time

import feedparser

STOP_WORDS = {
    "the", "a", "an", "is", "are", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "says", "after", "as", "its", "it",
    "by", "with", "from", "that", "this", "be", "has", "have", "had",
}


def fetch_rss(feed_url: str, source: str, limit: int = 15) -> list[dict]:
    items = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            title = entry.get("title", "").strip()
            url   = entry.get("link", "")
            if title:
                items.append({"title": title, "url": url, "source": source})
    except Exception as e:
        logging.error(f"{source} RSS 오류: {e}")
    return items


def is_duplicate(title: str, seen: list[str], threshold: int = 4) -> bool:
    words_new = set(title.lower().split()) - STOP_WORDS
    for seen_title in seen:
        words_ex = set(seen_title.lower().split()) - STOP_WORDS
        if len(words_new & words_ex) >= threshold:
            return True
    return False


def fetch_and_dedupe(sources: list[tuple], limit: int = 15) -> list[dict]:
    """여러 RSS 소스 수집 → 라운드로빈 인터리브 → 중복 제거 → limit개 반환"""
    buckets = []
    for source, url in sources:
        items = fetch_rss(url, source)
        buckets.append(items)
        time.sleep(0.3)

    # 소스별로 균등하게 섞기 (라운드로빈)
    interleaved = []
    max_len = max((len(b) for b in buckets), default=0)
    for i in range(max_len):
        for bucket in buckets:
            if i < len(bucket):
                interleaved.append(bucket[i])

    seen_titles = []
    deduped = []
    for item in interleaved:
        if not is_duplicate(item["title"], seen_titles):
            seen_titles.append(item["title"])
            deduped.append(item)
        if len(deduped) >= limit:
            break

    return deduped
