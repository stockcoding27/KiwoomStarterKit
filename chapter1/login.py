import requests
from config import api_key, api_secret_key, host


# 접근토큰 발급
def fn_au10001(data):
    endpoint = '/oauth2/token'
    url =  host + endpoint
    headers = {
        'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['token']


# 실행 구간
if __name__ == '__main__':
    # 1. 요청 데이터
    params = {
        'grant_type': 'client_credentials',  # grant_type
        'appkey': api_key,  # 앱키
        'secretkey': api_secret_key,  # 시크릿키
    }

    # 2. API 실행
    token = fn_au10001(data=params)
    # 토큰 print
    print(token)
