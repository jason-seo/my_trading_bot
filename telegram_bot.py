import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.last_update_id = None
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # 시작 시점의 최신 update_id를 가져와서 과거 메시지 무시 설정
        self._get_initial_update_id()

    def _get_initial_update_id(self):
        url = f"{self.base_url}/getUpdates"
        try:
            res = requests.get(url, params={"offset": -1}).json()
            if res.get("ok") and res.get("result"):
                self.last_update_id = res["result"][0]["update_id"] + 1
            else:
                self.last_update_id = 0
        except Exception as e:
            print(f"텔레그램 초기화 오류: {e}")
            self.last_update_id = 0

    def send_message(self, text):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"메시지 전송 오류: {e}")

    def get_updates(self):
        url = f"{self.base_url}/getUpdates"
        params = {"offset": self.last_update_id, "timeout": 10}
        try:
            response = requests.get(url, params=params, timeout=15).json()
            return response.get("result", [])
        except Exception as e:
            print(f"메시지 수신 오류: {e}")
            return []

    def update_id(self, next_id):
        self.last_update_id = next_id