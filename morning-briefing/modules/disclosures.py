"""DART OpenAPI 주요 공시 (OpenDartReader)"""
import logging
from datetime import datetime

import OpenDartReader

from config import DART_API_KEY


def fetch():
    result = []

    if not DART_API_KEY:
        logging.warning("DART_API_KEY 미설정 — 공시 수집 건너뜀")
        return result

    try:
        dart  = OpenDartReader(DART_API_KEY)
        today = datetime.today().strftime("%Y-%m-%d")

        # kind="": 전체 공시 / 필요 시 "A"(정기), "B"(주요사항) 등으로 좁힐 수 있음
        df = dart.list(start=today, kind="")

        if df is not None and not df.empty:
            for _, row in df.head(5).iterrows():
                rcept_no = row.get("rcept_no", "")
                result.append({
                    "company": row.get("corp_name", ""),
                    "title":   row.get("report_nm", ""),
                    "date":    row.get("rcept_dt", ""),
                    "url":     f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                })
    except Exception as e:
        logging.error(f"DART 공시 조회 오류: {e}")

    return result
