import requests
import json
import pandas as pd

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


# 계좌평가잔고내역요청
def fn_kt00018(token, data, cont_yn='N', next_key=''):
    # 1. 요청할 API URL
    endpoint = '/api/dostk/acnt'
    url =  host + endpoint

    # 2. header 데이터
    headers = {
        'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
        'authorization': f'Bearer {token}', # 접근토큰
        'cont-yn': cont_yn, # 연속조회여부
        'next-key': next_key, # 연속조회키
        'api-id': 'kt00018', # TR명
    }

    # 3. http POST 요청
    response = requests.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        # 에러를 response 내용까지 추가해서 출력
        error_message = f"HTTP Error: {e}\nResponse Body: {response.text}"
        raise requests.HTTPError(error_message) from e

    res = response.json()
    account_info_dict = dict(
        총매입금액=int(res['tot_pur_amt']),
        총평가금액=int(res['tot_evlt_amt']),
        총평가손익금액=int(res['tot_evlt_pl']),
        총수익률=float(res['tot_prft_rt']),
        추정예탁자산=int(res['prsm_dpst_aset_amt']),
    )
    df = pd.DataFrame(res['acnt_evlt_remn_indv_tot'])
    column_name_to_kor_name_map = {
        "stk_cd": "종목코드",
        "stk_nm": "종목명",
        "evltv_prft": "평가손익",
        "prft_rt": "수익률(%)",
        "pur_pric": "매입가",
        "pred_close_pric": "전일종가",
        "rmnd_qty": "보유수량",
        "trde_able_qty": "매매가능수량",
        "cur_prc": "현재가",
        "pred_buyq": "전일매수수량",
        "pred_sellq": "전일매도수량",
        "tdy_buyq": "금일매수수량",
        "tdy_sellq": "금일매도수량",
        "pur_amt": "매입금액",
        "pur_cmsn": "매입수수료",
        "evlt_amt": "평가금액",
        "sell_cmsn": "평가수수료",
        "tax": "세금",
        "sum_cmsn": "수수료합",
        "poss_rt": "보유비중(%)",
        "crd_tp": "신용구분",
        "crd_tp_nm": "신용구분명",
        "crd_loan_dt": "대출일",
    }
    df.rename(columns=column_name_to_kor_name_map, inplace=True)
    df["종목코드"] = df["종목코드"].apply(lambda x: x.replace("A", ""))
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return account_info_dict, df

# 실행 구간
if __name__ == '__main__':
    params = {
        'grant_type': 'client_credentials',  # grant_type
        'appkey': api_key,  # 앱키
        'secretkey': api_secret_key,  # 시크릿키
    }

    # 2. API 실행
    token = fn_au10001(data=params)

    # 2. 요청 데이터
    params = {
        'qry_tp': '1', # 조회구분 1:합산, 2:개별
        'dmst_stex_tp': 'KRX', # 국내거래소구분 KRX:한국거래소,NXT:넥스트트레이드
    }

    # 3. API 실행
    account_info_dict, df = fn_kt00018(token=token, data=params)
    print(account_info_dict)
    print(df.to_string())
