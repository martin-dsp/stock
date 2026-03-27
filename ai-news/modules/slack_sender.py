"""슬랙 메시지 포맷팅 + Incoming Webhook 발송"""
import logging
from datetime import datetime

import requests

from config import SLACK_WEBHOOK_URL

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _build_message(data: dict) -> str:
    now      = datetime.now()
    date_str = now.strftime(f"%Y-%m-%d ({WEEKDAY_KR[now.weekday()]})")

    lines = [f"*🤖 AI 데일리 뉴스 — {date_str}*", ""]

    articles = data.get("articles") or []
    if articles:
        for item in articles:
            source   = item.get("source", "")
            title_ko = item.get("title_ko") or item.get("title", "")
            url      = item.get("url", "")
            if url:
                lines.append(f"• [{source}] <{url}|{title_ko}>")
            else:
                lines.append(f"• [{source}] {title_ko}")
    else:
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
