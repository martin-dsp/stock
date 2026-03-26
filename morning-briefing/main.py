"""모닝 브리핑 진입점 — 각 모듈 독립 실행 후 슬랙 발송"""
import logging
import os
import sys

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/briefing.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

from modules import disclosures, futures, kr_market, news, slack_sender, us_markets

MODULES = [
    ("us_markets",   us_markets),
    ("futures",      futures),
    ("kr_market",    kr_market),
    ("news",         news),
    ("disclosures",  disclosures),
]


def main():
    logging.info("=== 모닝 브리핑 시작 ===")
    data = {}

    for name, module in MODULES:
        try:
            logging.info(f"{name} 수집 중...")
            data[name] = module.fetch()
            logging.info(f"{name} 완료")
        except Exception as e:
            logging.error(f"{name} 실패: {e}")
            data[name] = None

    slack_sender.send(data)
    logging.info("=== 모닝 브리핑 완료 ===")


if __name__ == "__main__":
    main()
