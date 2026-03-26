"""슬랙 메시지 포맷팅 + Incoming Webhook 발송"""
import logging
from datetime import datetime

import requests

from config import SLACK_WEBHOOK_URL

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _arrow(change_pct) -> str:
    if change_pct is None:
        return "-"
    if change_pct > 0:
        return f"▲ +{change_pct:.2f}%"
    if change_pct < 0:
        return f"▼ {change_pct:.2f}%"
    return f"- 0.00%"


def _build_message(data: dict) -> str:
    now = datetime.now()
    date_str = now.strftime(f"%Y-%m-%d ({WEEKDAY_KR[now.weekday()]})")

    lines = [f"*📊 모닝 브리핑 — {date_str}*", ""]

    # ── 미국 증시 마감 ────────────────────────────
    us = data.get("us_markets") or {}
    lines.append("*🇺🇸 미국 증시 마감*")
    for name in ("S&P500", "Nasdaq", "Dow Jones"):
        d = us.get(name)
        if d:
            lines.append(f"• {name}: {d['price']:,.2f}  {_arrow(d['change_pct'])}")
    d = us.get("USD/KRW")
    if d:
        lines.append(f"• USD/KRW: {d['price']:,.2f}원  {_arrow(d['change_pct'])}")
    lines.append("")

    # ── 야간선물 ──────────────────────────────────
    fut = data.get("futures") or {}
    if fut:
        lines.append("*📈 야간선물*")
        for name in ("KOSPI", "KOSDAQ", "S&P500 선물", "나스닥100 선물"):
            d = fut.get(name)
            if d:
                price = d.get("price", "N/A")
                lines.append(f"• {name}: {price}  {_arrow(d.get('change_pct'))}")
        lines.append("")

    # ── 거래량 상위 ───────────────────────────────
    kr = data.get("kr_market") or {}
    date_label = kr.get("date", "전일")
    if kr.get("volume_top"):
        lines.append(f"*🔥 거래량 상위 ({date_label})*")
        for i, item in enumerate(kr["volume_top"], 1):
            lines.append(
                f"{i}. {item['name']}  {item['price']:,}원  "
                f"{_arrow(item['change_pct'])}  ({item['volume']:,}주)"
            )
        lines.append("")

    # ── 급등 / 급락 ───────────────────────────────
    if kr.get("gainers") or kr.get("losers"):
        lines.append("*📊 급등 / 급락 상위*")
        if kr.get("gainers"):
            lines.append("_급등_")
            for item in kr["gainers"]:
                lines.append(f"• {item['name']}  {item['price']:,}원  {_arrow(item['change_pct'])}")
        if kr.get("losers"):
            lines.append("_급락_")
            for item in kr["losers"]:
                lines.append(f"• {item['name']}  {item['price']:,}원  {_arrow(item['change_pct'])}")
        lines.append("")

    # ── 국내 뉴스 ─────────────────────────────────
    news = data.get("news") or {}
    if news.get("domestic"):
        lines.append("*📰 국내 주요 뉴스*")
        for item in news["domestic"]:
            lines.append(f"• {item['title']}")
        lines.append("")

    # ── 해외 뉴스 ─────────────────────────────────
    if news.get("international"):
        lines.append("*🌐 해외 주요 뉴스*")
        for item in news["international"]:
            source = item.get("source", "")
            lines.append(f"• [{source}] {item['title']}")
        lines.append("")

    # ── 공시 ──────────────────────────────────────
    disclosures = data.get("disclosures") or []
    if disclosures:
        lines.append("*📋 주요 공시*")
        for item in disclosures:
            lines.append(f"• {item['company']} — {item['title']}")
        lines.append("")

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
