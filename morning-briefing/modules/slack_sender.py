"""슬랙 메시지 포맷팅 + Incoming Webhook 발송"""
import logging
from datetime import datetime

import requests

from config import SLACK_WEBHOOK_URL

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _arrow(change_pct) -> str:
    if change_pct is None:
        return "- N/A"
    if change_pct > 0:
        return f"▲ +{change_pct:.2f}%"
    if change_pct < 0:
        return f"▼ {change_pct:.2f}%"
    return "- 0.00%"


def _build_message(data: dict) -> str:
    now      = datetime.now()
    date_str = now.strftime(f"%Y-%m-%d ({WEEKDAY_KR[now.weekday()]})")

    lines = [f"*📊 모닝 브리핑 — {date_str}*", ""]

    # ── 미국 증시 마감 (전일 종가) ───────────────────────
    us = data.get("us_markets") or {}
    lines.append("*🇺🇸 미국 증시 마감 (전일)*")
    for name in ("S&P500", "Nasdaq", "Dow Jones"):
        d = us.get(name)
        if d:
            lines.append(f"• {name}: {d['price']:,.2f}  {_arrow(d['change_pct'])}")
    lines.append("")

    # ── 환율 (현재 실시간) ───────────────────────────────
    d = us.get("USD/KRW")
    if d:
        tag = "현재" if d.get("realtime") else "전일"
        lines.append(f"*💱 USD/KRW ({tag})*")
        lines.append(f"• {d['price']:,.2f}원  {_arrow(d['change_pct'])}")
        lines.append("")

    # ── 선물 / 지수 ──────────────────────────────────────
    fut = data.get("futures") or {}
    if fut:
        lines.append("*📈 선물 / 지수*")
        # 한국 지수 (전일 종가)
        for name in ("KOSPI", "KOSDAQ"):
            d = fut.get(name)
            if d:
                tag = "현재" if d.get("realtime") else "전일"
                lines.append(f"• {name} ({tag}): {d['price']}  {_arrow(d.get('change_pct'))}")
        # 미국 선물 (현재 실시간)
        for name in ("S&P500 선물", "나스닥100 선물"):
            d = fut.get(name)
            if d:
                tag = "현재" if d.get("realtime") else "전일"
                lines.append(f"• {name} ({tag}): {d['price']:,.2f}  {_arrow(d.get('change_pct'))}")
        lines.append("")

    # ── 거래량 상위 (전일) ───────────────────────────────
    kr = data.get("kr_market") or {}
    if kr.get("volume_top"):
        lines.append("*🔥 거래량 상위 — 전일 (KOSPI+KOSDAQ)*")
        for i, item in enumerate(kr["volume_top"], 1):
            mkt = item.get("market", "")
            lines.append(
                f"{i}. [{mkt}] {item['name']}  {item['price']:,}원  "
                f"{_arrow(item['change_pct'])}  ({item['volume']:,}주)"
            )
        lines.append("")

    # ── 급등 / 급락 (전일) ───────────────────────────────
    disclosures  = data.get("disclosures") or []
    disc_by_corp = {d["company"]: d for d in disclosures}

    def _render_mover(item: dict) -> list[str]:
        mkt    = item.get("market", "")
        code   = item.get("code", "")
        name   = item["name"]
        price  = item["price"]
        pct    = item["change_pct"]
        news   = item.get("news") or []

        stock_url = f"https://finance.naver.com/item/main.naver?code={code}" if code else ""
        name_str  = f"<{stock_url}|{name}>" if stock_url else name

        out = [f"• [{mkt}] {name_str}  {price:,}원  {_arrow(pct)}"]

        # DART 공시 매칭
        if name in disc_by_corp:
            d = disc_by_corp[name]
            disc_url = d.get("url", "")
            disc_txt = d["title"]
            out.append(f"  📋 공시: <{disc_url}|{disc_txt}>" if disc_url else f"  📋 공시: {disc_txt}")

        # 종목 뉴스
        for n in news:
            out.append(f"  📰 <{n['url']}|{n['title']}>" if n.get("url") else f"  📰 {n['title']}")

        return out

    if kr.get("gainers") or kr.get("losers"):
        lines.append("*📊 급등 / 급락 — 전일 각 10종목*")
        if kr.get("gainers"):
            lines.append("_급등_")
            for item in kr["gainers"]:
                lines.extend(_render_mover(item))
        if kr.get("losers"):
            lines.append("_급락_")
            for item in kr["losers"]:
                lines.extend(_render_mover(item))
        lines.append("")

    # ── 국내 뉴스 (링크 포함) ────────────────────────────
    news = data.get("news") or {}
    if news.get("domestic"):
        lines.append("*📰 국내 주요 뉴스*")
        for item in news["domestic"]:
            url   = item.get("url", "")
            title = item["title"]
            if url:
                lines.append(f"• <{url}|{title}>")
            else:
                lines.append(f"• {title}")
        lines.append("")

    # ── 해외 뉴스 (번역 + 링크) ──────────────────────────
    if news.get("international"):
        lines.append("*🌐 해외 주요 뉴스*")
        for item in news["international"]:
            source   = item.get("source", "")
            title_ko = item.get("title_ko") or item.get("title", "")
            url      = item.get("url", "")
            if url:
                lines.append(f"• [{source}] <{url}|{title_ko}>")
            else:
                lines.append(f"• [{source}] {title_ko}")
        lines.append("")

    # ── 공시 ─────────────────────────────────────────────
    disclosures = data.get("disclosures") or []
    if disclosures:
        lines.append("*📋 주요 공시*")
        for item in disclosures:
            url = item.get("url", "")
            txt = f"{item['company']} — {item['title']}"
            if url:
                lines.append(f"• <{url}|{txt}>")
            else:
                lines.append(f"• {txt}")
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
