"""영어 → 한국어 번역 래퍼 (Google Translate via deep-translator)"""
import logging
import time


def translate(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target="ko").translate(text[:500])
    except Exception as e:
        logging.warning(f"번역 실패: {e}")
        return text


def translate_batch(articles: list[dict]) -> list[dict]:
    """각 article의 title을 번역해 title_ko 추가"""
    for article in articles:
        article["title_ko"] = translate(article["title"])
        time.sleep(0.2)
    return articles
