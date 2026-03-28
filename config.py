import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 할당
LS_APP_KEY = os.getenv("LS_APP_KEY")
LS_APP_SECRET = os.getenv("LS_APP_SECRET")
LS_ACCOUNT_NO = os.getenv("LS_ACCOUNT_NO")
LS_ACCOUNT_PW = os.getenv("LS_ACCOUNT_PW", "")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# LS증권 실전투자 API 도메인 (모의투자의 경우 https://openapi.ls-sec.co.kr:28080 로 변경)
LS_DOMAIN = "https://openapi.ls-sec.co.kr:8080"

