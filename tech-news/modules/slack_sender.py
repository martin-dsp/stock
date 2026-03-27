"""슬랙 메시지 포맷팅 + Incoming Webhook 발송"""
import logging
from datetime import datetime

import requests

from config import SLACK_WEBHOOK_URL

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _build_message(data: dict) -> str:
    now      = datetime.now()
    date_str = now.strftime(f"%Y-%m-%d ({WEEKDAY_KR[now.weekday()]})")

    lines = [f"*💻 테크 뉴스 브리핑 — {date_str}*", ""]

    # HackerNews 섹션
    hn_articles = data.get("hackernews") or []
    if hn_articles:
        lines.append("*🔥 HackerNews 인기*")
        for item in hn_articles:
            title_ko = item.get("title_ko") or item.get("title", "")
            url      = item.get("url", "")
            points   = item.get("points", 0)
            comments = item.get("comments", 0)
            if url:
                lines.append(f"• <{url}|{title_ko}> (⬆ {points} | 💬 {comments})")
            else:
                lines.append(f"• {title_ko} (⬆ {points} | 💬 {comments})")
        lines.append("")

    # 테크 미디어 섹션
    tech_articles = data.get("tech_feeds") or []
    if tech_articles:
        lines.append("*📡 테크 미디어*")
        for item in tech_articles:
            source   = item.get("source", "")
            title_ko = item.get("title_ko") or item.get("title", "")
            url      = item.get("url", "")
            if url:
                lines.append(f"• [{source}] <{url}|{title_ko}>")
            else:
                lines.append(f"• [{source}] {title_ko}")

    if not hn_articles and not tech_articles:
        lines.append("뉴스를 가져오지 못했습니다.")

    return "\n".join(lines)


def send(data: dict) -> bool:
    if not SLACK_WEBHOOK_URL:
        logging.error("SLACK_WEBHOOK_URL 미설정 — 발송 불가")
        return False

    message = _build_message(data)

    try:
        resp = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=10,
        )
        if resp.status_code == 200:
            logging.info("슬랙 발송 성공")
            return True
        else:
            logging.error(f"슬랙 발송 실패: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logging.error(f"슬랙 발송 오류: {e}")
        return False
