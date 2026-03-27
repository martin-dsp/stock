"""AI 뉴스 RSS 수집 (Anthropic, OpenAI, TechCrunch AI, The Verge AI, MIT Tech Review)"""
from modules.rss_fetcher import fetch_and_dedupe
from modules.translator import translate_batch

RSS_SOURCES = [
    ("Anthropic",      "https://www.anthropic.com/rss.xml"),
    ("OpenAI",         "https://openai.com/blog/rss.xml"),
    ("TechCrunch AI",  "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI",   "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("MIT Tech Review","https://www.technologyreview.com/topic/artificial-intelligence/feed"),
]


def fetch() -> list[dict]:
    articles = fetch_and_dedupe(RSS_SOURCES, limit=15)
    translate_batch(articles)
    return articles
