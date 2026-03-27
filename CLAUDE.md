# CLAUDE.md

## 프로젝트 개요

주식 투자 자동화 도구 모음.

## 프로젝트 구조

- `morning-briefing/` — 한국 증시 모닝 브리핑 (평일 오전 8시 슬랙 발송)
- `ai-news/` — AI 데일리 뉴스 브리핑 (매일 오전 8시 슬랙 발송)
- `world-news/` — 세계 뉴스 데일리 브리핑 (매일 오전 8시 슬랙 발송)
- `tech-news/` — 테크/HackerNews 데일리 브리핑 (매일 오전 8시 슬랙 발송)
- `us-market-monitor/` — 미국 시장 모니터링 (예정, Macro-Pulse 기반)

각 서브 프로젝트는 독립적으로 실행 가능해야 함. 공유 의존성 없이 각자 requirements.txt 관리.

## 코드 스타일

- 변수명, 함수명, 클래스명: 영어
- 주석, 커밋 메시지, 문서: 한국어
- Python 코드는 가독성 우선 — 간결하게 작성

## Python 환경

- 각 서브 프로젝트마다 `.venv/` 가상환경을 만들어서 독립적으로 관리
- 가상환경 활성화 후 의존성 설치: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- `.venv/`는 gitignore 대상

## 환경 설정

- 시크릿은 `.env` 파일로 관리 (절대 커밋하지 말 것)

## 운영 환경

- GitHub Actions + 맥미니 셀프호스티드 러너로 상시 운영
- 로그는 각 서브 프로젝트의 `logs/` 디렉토리에 저장
