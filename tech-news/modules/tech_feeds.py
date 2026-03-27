"""테크 미디어 RSS 수집 (TechCrunch, Ars Technica)"""
from modules.rss_fetcher import fetch_and_dedupe
from modules.translator import translate_batch

RSS_SOURCES = [
    ("TechCrunch",   "https://techcrunch.com/feed/"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
]


def fetch() -> list[dict]:
    articles = fetch_and_dedupe(RSS_SOURCES, limit=10)
    translate_batch(articles)
    return articles
