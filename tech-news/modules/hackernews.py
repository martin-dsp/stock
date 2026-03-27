"""HackerNews 인기 글 수집 (Algolia API, 포인트순)"""
import logging

import requests

from modules.translator import translate_batch

HN_API_URL = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"


def fetch(limit: int = 15) -> list[dict]:
    try:
        resp = requests.get(HN_API_URL, timeout=10)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
    except Exception as e:
        logging.error(f"HackerNews API 오류: {e}")
        return []

    articles = []
    for hit in hits:
        title = hit.get("title", "").strip()
        url   = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        points   = hit.get("points") or 0
        comments = hit.get("num_comments") or 0
        if title:
            articles.append({
                "title":    title,
                "url":      url,
                "source":   "HackerNews",
                "points":   points,
                "comments": comments,
            })

    # 포인트 내림차순 정렬 후 limit개
    articles.sort(key=lambda x: x["points"], reverse=True)
    articles = articles[:limit]

    translate_batch(articles)
    return articles
