
import streamlit as st

import pandas as pd
import requests
from io import BytesIO

# Define the function that fetches data and returns a DataFrame
def get_data(inqryBgnDt, inqryEndDt):
    ServiceKey = 'UoG7nmaXg%2F8KPDyDthmkeKJ6rFMrECo2VVPv%2Fy0%2Ba2UcSA9D%2F0kNaIu2eqwDeSIch1YoWrARbG2c%2BHMfNUuZPA%3D%3D'

    # default setting
    info_version = "getScsbidListSttusCnstwkPPSSrch?inqryDiv=2"  # 데이터셋 개방표준에 따른 입찰공고정보
    PageNo = 1 # 페이지번호
    NumOfRows = 999 # 한 페이지 결과 수 , 최대 999개 이다.
    EndPoint = "http://apis.data.go.kr/1230000/ScsbidInfoService"
    Datatype = "json" # 오픈API 리턴 타입을 JSON으로 받고 싶을 경우 'json' 으로 지정함
    presmptPrceBgn =   500000000 # 추정가격시작
    presmptPrceEnd = 15000000000 # 추정가격종료
    region = 11 # 서울
    indstrytyCd = '0002' # 업종코드 0002
    
    Result_all =pd.DataFrame()
    nnn = 0
    while True:
        URL = f"{EndPoint}/{info_version}&indstrytyCd={indstrytyCd}&prtcptLmtRgnCd={region}&presmptPrceBgn={presmptPrceBgn}&presmptPrceEnd={presmptPrceEnd}&numOfRows={NumOfRows}&pageNo={PageNo}&inqryBgnDt={inqryBgnDt}0000&inqryEndDt={inqryEndDt}2359&ServiceKey={ServiceKey}&type={Datatype}"
        response = requests.get(URL)
        
        # 총 데이터 개수
        TotalCount = response.json()["response"]["body"]["totalCount"]

        # 나라장터 입찰공고 DataFrame 생성
        result_df = pd.DataFrame(response.json()["response"]["body"]["items"])
        
        # 읽은 데이터의 개수를 확인해서 데이터의 끝인지 확인
        if len(result_df) == 0 : break
        
        # 필요한 열만 선택
        selected_columns = ["bidNtceNo",  "bidNtceNm", "bidwinnrBizno", 'bidwinnrNm', "bidwinnrCeoNm", "sucsfbidAmt", "sucsfbidRate"]
        result_df = result_df[selected_columns].copy()  # 데이터프레임의 복사본 생성
        
        # 열 이름 변경
        result_df.rename(columns={"bidNtceNm": "공고명", "bidNtceNo": "공고번호", "bidwinnrBizno": "사업자 등록번호", 
                                  "bidwinnrNm": "업체명", "bidwinnrCeoNm": "대표자명",
                                 "sucsfbidAmt": "입찰금액(원)", "sucsfbidRate": "투찰률(%)"}, inplace=True)
        
        # 데이터 프레임 병합
        Result_all = pd.concat([Result_all,result_df],axis=0)
        Result_all.reset_index(drop=True,inplace=True)

        # 페이지 증가
        PageNo=str(int(PageNo)+1)
    return Result_all

# Define the function to get the details
def get_details(bidNtceNo):
    ServiceKey = 'UoG7nmaXg%2F8KPDyDthmkeKJ6rFMrECo2VVPv%2Fy0%2Ba2UcSA9D%2F0kNaIu2eqwDeSIch1YoWrARbG2c%2BHMfNUuZPA%3D%3D'

    # default setting
    info_version = "getOpengResultListInfoCnstwkPreparPcDetail?inqryDiv=2"  # 데이터셋 개방표준에 따른 입찰공고정보
    PageNo = 1 # 페이지번호
    NumOfRows = 999 # 한 페이지 결과 수 , 최대 999개 이다.
    EndPoint = "http://apis.data.go.kr/1230000/ScsbidInfoService"
    Datatype = "json" # 오픈API 리턴 타입을 JSON으로 받고 싶을 경우 'json' 으로 지정함
    
    Result_detail =pd.DataFrame()
    nnn = 0
    while True:
        URL = f"{EndPoint}/{info_version}&pageNo={PageNo}&numOfRows={NumOfRows}&bidNtceNo={bidNtceNo}&ServiceKey={ServiceKey}&type={Datatype}"
        response = requests.get(URL)
        
        # 총 데이터 개수
        TotalCount = response.json()["response"]["body"]["totalCount"]

        # 나라장터 입찰공고 DataFrame 생성
        result_detail_df = pd.DataFrame(response.json()["response"]["body"]["items"])
        
        # 읽은 데이터의 개수를 확인해서 데이터의 끝인지 확인
        if len(result_detail_df) == 0 : break
        
        # 필요한 열만 선택
        selected_columns = ["bidNtceNo",  "bidNtceOrd", 'rbidNo', "rlOpengDt", "bssamt", "plnprc", 
                            "PrearngPrcePurcnstcst"]
        result_detail_df = result_detail_df[selected_columns].copy()  # 데이터프레임의 복사본 생성
        
        # 열 이름 변경
        result_detail_df.rename(columns={"bidNtceNo": "공고번호", "bidNtceOrd": "입찰공고차수", "rbidNo": "재입찰번호", 
                                         "rlOpengDt": "실개찰일시", "plnprc": "예정가격", "bssamt": "기초금액", 
                                         "bsisPlnprc": "기초예정가격", "PrearngPrcePurcnstcst": "예정가격순공사비"}, inplace=True)
        
        # 데이터 프레임 병합
        Result_detail = pd.concat([Result_detail,result_detail_df],axis=0)
        Result_detail.reset_index(drop=True,inplace=True)

        # 페이지 증가
        PageNo=str(int(PageNo)+1)
    
    
    Result_detail_unique = Result_detail.drop_duplicates(subset=['공고번호'])

    return Result_detail_unique

    

# Streamlit application
def main():
    st.title("개찰완료 데이터 조회")

    # User inputs for the start and end dates
    inqryBgnDt = st.text_input("시작 일자 (YYYYMMDD):", "20230101")
    inqryEndDt = st.text_input("종료 일자 (YYYYMMDD):", "20230131")

    # Button to fetch the data
    if st.button("조회하기"):
        with st.spinner("데이터를 불러오는 중..."):
            # Fetch the main data
            result_all = get_data(inqryBgnDt, inqryEndDt)

            # Fetch the details for each unique bid number
            result_detail_final = pd.DataFrame()
            for i in result_all["공고번호"].unique():
                temp = get_details(i)
                result_detail_final = pd.concat([result_detail_final, temp], axis=0)

            # Merge the results
            result_all = result_all.merge(result_detail_final, on='공고번호', how='left')

            # Convert the final result to a bytes object
            towrite = BytesIO()
            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                result_all.to_excel(writer, index=False)
            towrite.seek(0)

            # Download link for the data
            st.success('데이터 불러오기 완료!')
            st.download_button(label='📥 다운로드: Excel 파일', 
                               data=towrite, 
                               file_name='result.xlsx', 
                               mime='application/vnd.ms-excel')

if __name__ == "__main__":
    main()
