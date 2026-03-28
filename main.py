import schedule
import requests
import time
from datetime import datetime
from ls_api import get_access_token, get_account_balance, execute_condition_search, get_condition_list
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from telegram_bot import TelegramBot

# 봇 객체 생성
bot = TelegramBot()

def job_scheduled_balance():
    token = get_access_token()
    balance_info = get_account_balance(token)
    bot.send_message(f"⏰ [정기 알림]\n{balance_info}")

# 매일 특정 시간 스케줄 (예: 오후 3시 30분)
schedule.every().day.at("15:30").do(job_scheduled_balance)

if __name__ == "__main__":
    print("🚀 LS증권 알림 & 실시간 챗봇 감시 시작...")
    bot.send_message("🤖 봇이 가동되었습니다. 명령어(/잔액, /조건식명)를 입력하세요.")

    while True:
        # 1. 스케줄러 실행 (예정된 작업이 있으면 수행)
        schedule.run_pending()

        # 2. 텔레그램 메시지 실시간 감시 (Long Polling)
        updates = bot.get_updates()
        for update in updates:
            # 다음 메시지를 위해 ID 업데이트
            bot.update_id(update["update_id"] + 1)
            
            if "message" not in update or "text" not in update["message"]:
                continue
                
            chat_id = str(update["message"]["chat"]["id"])
            text = update["message"]["text"].strip()

            # 본인 계정인지 확인 (보안)
            if chat_id != bot.chat_id:
                continue

            print(f"📩 수신된 메시지: {text}")

            # 명령어 판별
            if text == "/잔액":
                token = get_access_token()
                result = get_account_balance(token)
                bot.send_message(result)

            elif text == "/목록":  # <--- 새로운 명령어 추가
                token = get_access_token()
                bot.send_message("📂 서버에서 조건식 목록을 가져오고 있습니다...")
                result = get_condition_list(token)
                bot.send_message(result)
            
            elif text.startswith("/"):
                cond_name = text[1:].strip()
                if not cond_name: continue
                
                token = get_access_token()
                bot.send_message(f"🔍 '{cond_name}' 검색 실행 중...")
                result = execute_condition_search(token, cond_name)
                bot.send_message(result)

        # CPU 과점유 방지를 위한 아주 짧은 휴식
        time.sleep(0.1)

def job_check_balance():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 잔액 확인 작업 실행 중...")
    
    # 1. API 토큰 발급
    token = get_access_token()
    if not token:
        send_telegram_message("⚠️ LS증권 API 토큰 발급 실패. 서버 상태를 확인하세요.")
        return

    # 2. 계좌 잔액 조회
    balance_info = get_account_balance(token)
    
    # 3. 텔레그램 메시지 전송
    message = f"📊 [LS증권 자동 잔고 알림]\n{balance_info}"
    send_telegram_message(message)
    print("텔레그램 알림 전송 완료.")

# 스케줄러 설정 (원하는 시간으로 수정 가능)
# 예: 매일 오후 3시 30분 (장 마감 직후)에 실행
schedule.every().day.at("01:05").do(job_check_balance)

if __name__ == "__main__":
    print("🤖 LS증권 계좌 알림 봇이 시작되었습니다.")
    
    # (선택) 시작하자마자 테스트용으로 1회 즉시 실행해보고 싶다면 아래 주석을 해제하세요.
    # job_check_balance() 
    
    # 설정된 시간까지 대기하며 무한 루프
    while True:
        schedule.run_pending()
        time.sleep(1)

LAST_UPDATE_ID = None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def handle_updates():
    """텔레그램 메시지 수신 및 명령어 처리"""
    global LAST_UPDATE_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"offset": LAST_UPDATE_ID, "timeout": 10}
    
    try:
        response = requests.get(url, params=params).json()
        for update in response.get("result", []):
            LAST_UPDATE_ID = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "")
            chat_id = str(message.get("chat", {}).get("id", ""))

            # 본인 채팅방 확인 (보안)
            if chat_id != TELEGRAM_CHAT_ID:
                continue

            # 명령어 처리
            if text == "/잔액":
                token = get_access_token()
                result = get_account_balance(token)
                send_telegram_message(result)
            
            elif text.startswith("/"):
                cond_name = text[1:].strip() # "/" 제외한 이름
                if cond_name == "start": continue # 기본명령어 제외
                
                token = get_access_token()
                send_telegram_message(f"🔍 '{cond_name}' 검색식을 실행합니다...")
                result = execute_condition_search(token, cond_name)
                send_telegram_message(result)
                
    except Exception as e:
        print(f"Error handling updates: {e}")

def job_scheduled_balance():
    token = get_access_token()
    balance_info = get_account_balance(token)
    send_telegram_message(f"⏰ [정기 알림]\n{balance_info}")

# 스케줄 설정
schedule.every().day.at("01:59").do(job_scheduled_balance)

if __name__ == "__main__":
    print("🤖 LS증권 알림 & 챗봇 가동 중...")
    
    while True:
        # 1. 스케줄러 체크
        schedule.run_pending()
        
        # 2. 텔레그램 메시지 체크 (실시간 응답)
        handle_updates()
        
        time.sleep(1)