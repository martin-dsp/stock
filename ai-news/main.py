"""AI 뉴스 브리핑 진입점"""
import logging
import os
import sys

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/ai-news.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

from modules import ai_feeds, slack_sender

MODULES = [
    ("articles", ai_feeds),
]


def main():
    logging.info("=== AI 뉴스 시작 ===")
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
    logging.info("=== AI 뉴스 완료 ===")


if __name__ == "__main__":
    main()
