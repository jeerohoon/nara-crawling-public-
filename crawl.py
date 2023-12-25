import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import datetime, time
from time import localtime, strftime
from datetime import timedelta
from tqdm import trange
import time

import re

def page_scrapping(url_pre, page_no):
    page_no_str = str(page_no)
    url = url_pre + page_no_str
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')
    content_link = []
    for i in html.select('td.tl > div > a'):
        content_link.append(i['href'])
    df = pd.read_html(url)[0]
    df = df[df['업무'].notnull()]
    
    return df

def basic_amount(xpath):
    try: 
        basic_amount_button = driver.find_element(By.XPATH, xpath)
        basic_amount_button.click()

        # 새 창/팝업으로 전환 (새 창/팝업이 열리는 경우)
        driver.switch_to.window(driver.window_handles[-1])

        # 새 페이지 로드를 위해 대기
        time.sleep(0.1)  # 페이지가 로드될 때까지 충분한 시간을 기다립니다.

        # 현재 페이지의 HTML 소스 가져오기
        html_source = driver.page_source

        # 페이지의 모든 테이블을 DataFrame으로 추출
        tables = pd.read_html(html_source)


        pre_price_basic = tables[0].iloc[2,3]       # 예비가격 기초금액
        pre_price_basic_cost = tables[0].iloc[3,3]  # 예비가격 기초금액 중 순공사원가
        a_value = tables[0].iloc[5,3]  # A 금액

        # 정규 표현식을 사용하여 숫자만 추출
        # \d+ 는 하나 이상의 숫자를 의미하며, 쉼표(,)와 공백을 제거합니다.
        pre_price_basic_temp = re.sub(r'[^\d]', '', pre_price_basic.split('(')[0])
        pre_price_basic_cost_temp = re.sub(r'[^\d]', '', pre_price_basic_cost.split('원')[0])
        a_value_temp = re.sub(r'[^\d]', '', a_value.split('원')[0])

        # 문자열을 정수로 변환

        pre_price_basic_int = int(pre_price_basic_temp)
        pre_price_basic_cost_int = int(pre_price_basic_cost_temp)
        a_value_temp_int = int(a_value_temp)

        # 세개의 값을 딕셔너리에 추가

        return {
            '예비가격 기초금액': pre_price_basic_int,
            '예비가격 기초금액 중 순공사원가': pre_price_basic_cost_int,
            'A 금액': a_value_temp_int
            }
    
    except NoSuchElementException:
        return None

def open_bid(xpath):
    try: 
        ### 1) 개찰완료 > 입찰 업체 리스트 조회 후 1순위 데이터 가져오기

        open_bid_button = driver.find_element(By.XPATH, xpath)
        open_bid_button.click()

        # 새 창/팝업으로 전환 (새 창/팝업이 열리는 경우)
        driver.switch_to.window(driver.window_handles[-1])

        # 새 페이지 로드를 위해 대기
        time.sleep(0.1)  # 페이지가 로드될 때까지 충분한 시간을 기다립니다.

        # 현재 페이지의 HTML 소스 가져오기
        html_source_complete = driver.page_source

        # 페이지의 모든 테이블을 DataFrame으로 추출
        tables_complete = pd.read_html(html_source_complete)

        biz_number = None
        company_name = None
        representative_name = None
        bid_amount = None
        bid_rate = None
        bid_difference = None
            
        # 일반적인 경우, 테이블이 2개
        if len(tables_complete) == 2 and len(tables_complete[1].columns) > 4:
            biz_number = tables_complete[1].iloc[0, 1]
            company_name = tables_complete[1].iloc[0, 2]
            representative_name = tables_complete[1].iloc[0, 3]
            bid_amount = tables_complete[1].iloc[0, 4]
            bid_rate = tables_complete[1].iloc[0, 5]
            bid_difference = tables_complete[1].iloc[0, 6]
        
        # 업체가 포기했을 경우, 테이블이 하나가 늘어남
        elif len(tables_complete) == 3 and len(tables_complete[2].columns) > 4:
            biz_number = tables_complete[2].iloc[0, 1]
            company_name = tables_complete[2].iloc[0, 2]
            representative_name = tables_complete[2].iloc[0, 3]
            bid_amount = tables_complete[2].iloc[0, 4]
            bid_rate = tables_complete[2].iloc[0, 5]
            bid_difference = tables_complete[2].iloc[0, 6]
            
        else:
            biz_number = None
            company_name = None
            representative_name = None
            bid_amount = None
            bid_rate = None
            bid_difference = None
        
        
        pre_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/form[1]/div[2]/table/tbody/tr[5]/td[2]/div/a/span')
                                                    
        pre_button.click()

        # 새 창/팝업으로 전환 (새 창/팝업이 열리는 경우)
        driver.switch_to.window(driver.window_handles[-1])

        # 새 페이지 로드를 위해 대기
        time.sleep(0.1)  # 페이지가 로드될 때까지 충분한 시간을 기다립니다.

        # 현재 페이지의 HTML 소스 가져오기
        html_source = driver.page_source

        # 페이지의 모든 테이블을 DataFrame으로 추출
        tables = pd.read_html(html_source)
        
        estimated_price = None
        estimated_price_cost = None
        
        if len(tables) > 2 and len(tables[2]) > 0 and len(tables[2].columns) > 1:
            estimated_price = tables[2].iloc[0,1] # 예정가격
        if len(tables) > 3 and len(tables[3]) > 0 and len(tables[3].columns) > 1:
            estimated_price_cost = tables[3].iloc[0,1] # 예정가격 중 순공사원가
        
#         estimated_price = tables[2].iloc[0,1] # 예정가격
#         estimated_price_cost = tables[3].iloc[0,1] # 예정가격 중 순공사원가
            
        return {
            '사업자 등록번호': biz_number,
            '업체명': company_name,
            '대표자명': representative_name,
            '입찰금액(원)': bid_amount,
            '투찰률(%)': bid_rate,
            '(입찰가격-A)(예정가격-A) *100': bid_difference,
            '예정가격': estimated_price,
            '예정가격 중 순공사원가': estimated_price_cost # 예정가격 중 순공사원가
            }
    
    except NoSuchElementException:
        return None

def run_scraper(input_date, input_days):

    low_limit = 500000000
    high_limit = 15000000000

    # 입력된 날짜를 datetime 객체로 변환
    d = datetime.datetime.strptime(input_date, '%Y%m%d').date()

    # 입력된 일수를 사용하여 timedelta 객체 생성
    td = timedelta(days=input_days)

    # 계산된 기간으로 fromBidDt와 toBidDt 설정
    fromBidDt = "20" + (d - td).strftime("%y/%m/%d")
    toBidDt = "20" + d.strftime("%y/%m/%d")

    print("조회 시작 날짜:", fromBidDt)
    print("조회 종료 날짜:", toBidDt)

    # URL 설정
    url_one = 'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?area=11&areaNm=&bidNm=&bidSearchType=1&budgetCompare=&detailPrdnm=&detailPrdnmNo=&fromBidDt='
    url_two = '&fromOpenBidDt=&industry=&industryCd=0002&instNm=&instSearchRangeType=&intbidYn=&orgArea=&procmntReqNo=&radOrgan=1&recordCountPerPage=100&refNo=&regYn=Y&searchDtType=1&searchType=1&strArea=&taskClCds=&toBidDt='
    url_three = '&toOpenBidDt=&useTotalCount=Y&currentPageNo='

    url_pre = url_one + fromBidDt + '&upBudget=' + str(low_limit) +'&downBudget=' + str(high_limit) + url_two + toBidDt + url_three

    print(url_pre)
    # 입찰공고 조회시 마지막 페이지 번호 찾기
    response = requests.get(url_pre + str(1)) 
    html = BeautifulSoup(response.text, 'html.parser')

    try : 
        last_page_no = html.select('#pagination > a.next_end')[0]['href'].split('=')[-1]

    except :
        last_page_no = 1 # 또는 적절한 기본값 설정
        
    print(last_page_no) # 입찰공고 조회시 마지막 페이지 번호

    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    basic_data = pd.DataFrame({col: [] for col in page_scrapping(url_pre, 1).columns}) # # 컬럼명은 사용하되 값은 비워둔 새 DataFrame 생성
    additional_data = [] # 기초금액조회 관련
    completed_data = [] # 개찰완료 관련
    expected_data = [] # 개찰완료 > 예정가격 관련

    for i in trange(1, (int(last_page_no)+1)):
        
        # 데이터 수집 및 처리
        df = page_scrapping(url_pre, i)
        time.sleep(0.1) # 페이지가 로드될 때까지 충분한 시간을 기다립니다.
        # Extracting the dates into separate columns
        df[['공고일자', '입찰일자']] = df['입력일시 (입찰마감일시)'].str.extract(r'(\d{4}/\d{2}/\d{2}) \d{2}:\d{2} \((\d{4}/\d{2}/\d{2}) \d{2}:\d{2}\)')
        
        basic_data = pd.concat([basic_data, df], ignore_index = True)

        
        
    for url in basic_data['내용링크']:

        # 기초금액조회 버튼 클릭
        driver.get(url)
        result_basic = basic_amount('/html/body/div[2]/div[2]/div[16]/table/tbody/tr/td[4]/a/span')

        if result_basic is None:
            result_basic = basic_amount('/html/body/div[2]/div[2]/div[17]/table/tbody/tr/td[4]/a/span')
        if result_basic is None:
            result_basic = basic_amount('/html/body/div[2]/div[2]/div[18]/table/tbody/tr/td[4]/a/span')
            
        if result_basic is None:
            result_basic = {
                '예비가격 기초금액': None,
                '예비가격 기초금액 중 순공사원가': None,
                'A 금액': None
            }
        additional_data.append(result_basic)

        # 개찰완료 데이터 

    for url in basic_data['내용링크']:
        driver.get(url)
        result = open_bid('/html/body/div[2]/div[2]/div[24]/table/tbody/tr/td[5]/a')
        if result is None:
            result = open_bid('/html/body/div[2]/div[2]/div[25]/table/tbody/tr/td[5]/a/span')
        if result is None:
            result = open_bid('/html/body/div[2]/div[2]/div[26]/table/tbody/tr/td[5]/a/span')

        if result is None:
            result = open_bid('//button[text()="개찰완료"]')
        if result is None:
            result = {
                '사업자 등록번호': None,
                '업체명': None,
                '대표자명': None,
                '입찰금액(원)': None,
                '투찰률(%)': None,
                '(입찰가격-A)(예정가격-A) *100': None,
                '예정가격': None,
                '예정가격 중 순공사원가': None
            }
        completed_data.append(result)

    driver.quit()

    # 세개 데이터를 DataFrame으로 변환
    additional_rows_df = pd.DataFrame(additional_data)
    #expected_data_df = pd.DataFrame(expected_data)
    completed_data_df = pd.DataFrame(completed_data)

    # 네개 DataFrame의 인덱스를 리셋
    basic_data_reset = basic_data.reset_index(drop=True)
    #expected_data_df = expected_data_df.reset_index(drop=True)
    additional_rows_df_reset = additional_rows_df.reset_index(drop=True)
    completed_data_df_reset = completed_data_df.reset_index(drop=True)

    # 인덱스를 리셋한 DataFrame을 병합
    combined_df = pd.concat([basic_data_reset, additional_rows_df_reset, completed_data_df_reset ], axis=1) # expected_data_df,
    return combined_df

# Download link for the data
st.success('데이터 불러오기 완료!')
st.download_button(label='📥 다운로드: Excel 파일', 
                    data=towrite, 
                    file_name='result.xlsx', 
                    mime='application/vnd.ms-excel')


st.title("공고일자 기준 공고 리스트 조회")

# 사용자 입력 받기
input_date = st.text_input("조회 종료일자를 입력하세요 (예: 20231212): ")
input_days = st.number_input("조회 기간(일수)을 입력하세요 (예: 3): ", min_value=1, value=3)

if st.button('조회하기'):
    result_df = run_scraper(input_date, input_days)
    st.dataframe(result_df)
    st.download_button(label='📥 다운로드: Excel 파일', data=result_df.to_excel().encode('utf-8'), file_name='data.xlsx', mime='application/vnd.ms-excel')

    