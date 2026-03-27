"""세계 뉴스 RSS 수집 (BBC, The Guardian, Al Jazeera, NPR)"""
from modules.rss_fetcher import fetch_and_dedupe
from modules.translator import translate_batch

RSS_SOURCES = [
    ("BBC",         "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("The Guardian","https://www.theguardian.com/world/rss"),
    ("Al Jazeera",  "https://www.aljazeera.com/xml/rss/all.xml"),
    ("NPR",         "https://feeds.npr.org/1001/rss.xml"),
]


def fetch() -> list[dict]:
    articles = fetch_and_dedupe(RSS_SOURCES, limit=15)
    translate_batch(articles)
    return articles
