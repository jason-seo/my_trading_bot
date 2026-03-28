import requests
import json
from config import LS_APP_KEY, LS_APP_SECRET, LS_ACCOUNT_NO, LS_ACCOUNT_PW, LS_DOMAIN

def get_access_token():
    """LS증권 API Access Token 발급"""
    url = f"{LS_DOMAIN}/oauth2/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "appkey": LS_APP_KEY,
        "appsecretkey": LS_APP_SECRET,
        "scope": "oob"
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"토큰 발급 실패: {response.text}")
        return None

def get_account_balance(access_token):
    """t0424(주식잔고조회)를 통한 계좌 추정 자산 파악"""
    url = f"{LS_DOMAIN}/stock/accno"
    
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "tr_cd": "t0424", 
        "tr_cont": "N",
        "mac_address": ""
    }
    
    data = {
        "t0424InBlock": {
            "prcgb": "1",    # 단가구분 (1: 평균단가)
            "chegb": "2",    # 체결구분 (2: 체결기준)
            "dangb": "0",    # 단일가구분 (0: 정규장)
            "charge": "1",   # 제비용포함여부 (1: 포함)
            "cts_expcode": "",
            "expcode": "",
            "accno": LS_ACCOUNT_NO,
            "passwd": LS_ACCOUNT_PW
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        
        # OutBlock에서 자산 데이터 추출
        out_block = result.get("t0424OutBlock", {})
        total_asset = out_block.get("sunamt", "0")   # 추정순자산
        total_profit = out_block.get("dtsunik", "0") # 실현손익
        
        # 포맷팅하여 문자열 반환
        try:
            total_asset_formatted = f"{int(total_asset):,}원"
        except (ValueError, TypeError):
            total_asset_formatted = f"{total_asset}원"

        return f"✅ 현재 계좌 추정 자산: {total_asset_formatted}\n당일 실현 손익: {total_profit}원"
    else:
        return f"❌ 잔고 조회 실패: {response.text}"
    
    
# def get_condition_list(access_token):
#     """서버에 저장된 조건검색식 목록 조회 (t1859)"""
#     url = f"{LS_DOMAIN}/stock/item-search"
#     headers = {
#         "content-type": "application/json; charset=utf-8",
#         "authorization": f"Bearer {access_token}",
#         "tr_cd": "t1859",
#         "tr_cont": "N"
#     }
#     # t1859InBlock은 비워두거나 기본값 전송
#     data = {"t1859InBlock": {"query_index": "0"}}
    
#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code == 200:
#         return response.json().get("t1859OutBlock", [])
#     return []

# def get_condition_list(access_token):
#     """서버에 저장된 조건검색식 목록 조회 (t1859)"""
#     url = f"{LS_DOMAIN}/stock/item-search"
#     headers = {
#         "content-type": "application/json; charset=utf-8",
#         "authorization": f"Bearer {access_token}",
#         "tr_cd": "t1859",
#         "tr_cont": "N"
#     }
#     # t1859InBlock: query_index는 보통 0으로 설정
#     data = {"t1859InBlock": {"query_index": "0"}}
    
#     try:
#         response = requests.post(url, headers=headers, json=data, timeout=10)
#         if response.status_code == 200:
#             result = response.json()
#             # t1859OutBlock은 리스트 형태로 반환됨
#             cond_list = result.get("t1859OutBlock", [])
#             if not cond_list:
#                 return "📁 저장된 조건검색식이 없습니다."
            
#             res_msg = "📋 [저장된 조건검색식 목록]\n"
#             for cond in cond_list:
#                 # nm: 조건명, index: 조건번호
#                 res_msg += f"- {cond['nm'].strip()} (ID: {cond['index']})\n"
#             res_msg += "\n💡 위 이름 중 하나를 '/이름' 형태로 입력하세요."
#             return res_msg
#         else:
#             return f"❌ 목록 조회 실패: {response.text}"
#     except Exception as e:
#         return f"❌ API 연결 오류: {str(e)}"


def get_condition_list(access_token):
    """서버에 저장된 조건검색식 목록 조회 (t1859)"""
    url = f"{LS_DOMAIN}/stock/item-search"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "tr_cd": "t1859",
        "tr_cont": "N"
    }
    data = {"t1859InBlock": {"query_index": "0"}}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # 성공 시 데이터 리스트(List) 반환
            return result.get("t1859OutBlock", [])
        else:
            return f"목록 조회 실패: {response.text}"
    except Exception as e:
        return f"연결 오류: {str(e)}"


# def execute_condition_search(access_token, condition_name):
#     """조건검색식 이름으로 종목 검색 실행 (t1857)"""
#     # 1. 먼저 조건식 목록에서 해당 이름의 인덱스/번호를 찾음
#     cond_list = get_condition_list(access_token)
#     target_index = None
#     for cond in cond_list:
#         if cond['nm'].strip() == condition_name.strip():
#             target_index = cond['index']
#             break
    
#     if target_index is None:
#         return f"❌ '{condition_name}' 조건식을 찾을 수 없습니다."

#     # 2. 해당 인덱스로 종목 조회
#     url = f"{LS_DOMAIN}/stock/item-search"
#     headers = {
#         "content-type": "application/json; charset=utf-8",
#         "authorization": f"Bearer {access_token}",
#         "tr_cd": "t1857",
#         "tr_cont": "N"
#     }
#     data = {
#         "t1857InBlock": {
#             "s_index": target_index,
#             "s_type": "0" # 0:전체
#         }
#     }
    
#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code == 200:
#         result = response.json()
#         items = result.get("t1857OutBlock1", [])
#         if not items:
#             return f"🔍 '{condition_name}' 검색 결과가 없습니다."
        
#         res_msg = f"📈 [{condition_name}] 검색 결과:\n"
#         for i, item in enumerate(items[:15]): # 상위 15개만 표시
#             res_msg += f"{i+1}. {item['hname']}({item['shcode']}) | 현재가: {int(item['price']):,}\n"
#         return res_msg
#     else:
#         return f"❌ 조건검색 실행 오류: {response.text}"

def execute_condition_search(access_token, condition_name):
    """조건검색식 이름으로 종목 검색 실행 (t1857)"""
    # 1. 먼저 조건식 목록을 가져옴
    cond_data = get_condition_list(access_token)
    
    # get_condition_list가 에러 메시지(문자열)를 반환했는지 확인
    if isinstance(cond_data, str):
        return cond_data # 에러 메시지 그대로 반환
    
    target_index = None
    # cond_data가 리스트인지 확인 후 루프 실행
    if isinstance(cond_data, list):
        for cond in cond_data:
            # 데이터가 사전 형식인지 한 번 더 확인 (안전장치)
            if isinstance(cond, dict) and 'nm' in cond:
                if cond['nm'].strip() == condition_name.strip():
                    target_index = cond['index']
                    break
    
    if target_index is None:
        return f"❌ '{condition_name}' 조건식을 찾을 수 없습니다. (/목록 명령어로 이름을 확인하세요)"

    # 2. 해당 인덱스로 종목 조회 (이후 코드는 동일)
    url = f"{LS_DOMAIN}/stock/item-search"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "tr_cd": "t1857",
        "tr_cont": "N"
    }
    data = {
        "t1857InBlock": {
            "s_index": target_index,
            "s_type": "0" # 0:전체
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            items = result.get("t1857OutBlock1", [])
            if not items:
                return f"🔍 '{condition_name}' 검색 결과가 없습니다."
            
            res_msg = f"📈 [{condition_name}] 검색 결과:\n"
            for i, item in enumerate(items[:15]): 
                res_msg += f"{i+1}. {item['hname']}({item['shcode']}) | 현재가: {int(item['price']):,}\n"
            return res_msg
        else:
            return f"❌ 조건검색 실행 오류: {response.text}"
    except Exception as e:
        return f"❌ 시스템 오류: {str(e)}"