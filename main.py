from database.postgres import connect_postgres, insert_news_data, get_last_pubdate_from_db
from processing.preprocess import clean_html, convert_date
from services.api_service import get_sentiment, fetch_news_data
from database.redshift import insert_data_to_redshift, fetch_new_data_from_postgres
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import urllib.request
import urllib.parse
from datetime import datetime
import logging



# 환경 변수 로드
load_dotenv(dotenv_path="/Users/imseungmin/project/.env")

# PostgreSQL 관련 환경 변수
db_host = 'localhost'
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_name = os.getenv("db_name")

# GPT API 관련 환경 변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 네이버 API 관련 환경 변수
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
# 루트 로거에 대한 설정
log_file_path = os.path.expanduser('~/project/app.log')
logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 포맷 설정
    handlers=[
        logging.FileHandler(log_file_path),  # 로그 파일 핸들러 추가
        logging.StreamHandler()  # 콘솔 핸들러 추가
    ]
)
# 환경 변수가 제대로 로드되었는지 확인
missing_vars = [var for var in ['client_id', 'client_secret', 'db_host', 'db_user', 'db_password', 'db_name', 'OPENAI_API_KEY'] if os.getenv(var) is None]
if missing_vars:
    logging.error(f"필수 환경 변수가 로드되지 않았습니다. {', '.join(missing_vars)}")
    pass




def main():
    try:
        with connect_postgres(db_host, db_user, db_password, db_name) as conn:# Postgres 연결

            if conn:
                fetch_limit = 100  # 페이지 개수 (최대 가져올 페이지 수)
                display = 1       # 한 번에 가져올 뉴스 개수
                start = 1          # 첫 번째 페이지 시작 번호
                encText = urllib.parse.quote("정치")  # 검색어 설정 및 URL 인코딩

                # DB에서 가장 최근의 pubDate 가져오기
                last_pubdate = get_last_pubdate_from_db(conn)
                logging.info(f"DB에서 가장 최근의 pubDate: {last_pubdate}")

                # # 필터링 기준 날짜를 수동으로 설정
                # filtered_date = "2024-09-01 00:00:00"
                # manual_pubdate = datetime.strptime(filtered_date, "%Y-%m-%d %H:%M:%S")

                for page in range(fetch_limit):
                    # 뉴스 데이터를 가져오기
                    news_data = fetch_news_data(client_id, client_secret, encText, start + page * display, display)

                    if not news_data:
                        logging.warning("가져온 뉴스 데이터가 없습니다.")
                        break

                    # 가장 최근 pubDate 이후의 뉴스만 필터링
                    filtered_news = []
                    for item in news_data:
                        news_pubdate = convert_date(item['pubDate'])
                        news_pubdate_datetime = datetime.strptime(news_pubdate, "%Y-%m-%d %H:%M:%S")
                        logging.info(f"뉴스 날짜: {news_pubdate_datetime}")

                        # last_pubdate에 도달하면 데이터 가져오기를 중단
                        if last_pubdate and news_pubdate_datetime <= last_pubdate:
                            logging.info(f"마지막 날짜 {last_pubdate}에 도달했습니다. 가져오기를 중단합니다.")
                            return
                            
                            
                        #     return
                        # 수동 설정한 날짜 이후의 뉴스만 필터링
                        # if news_pubdate_datetime < manual_pubdate:
                        #     logging.info(f"수동 설정한 날짜 {manual_pubdate} 에 도달했습니다. 가져오기를 중단합니다.")
                        #     continue

                        filtered_news.append(item)

                    logging.info(f"필터링된 뉴스 개수: {len(filtered_news)}")
    

                    for item in filtered_news:
                        title_cleaned = clean_html(item['title'])
                        description_cleaned = clean_html(item['description'])
                        pubDate_cleaned = convert_date(item['pubDate'])

                        # GPT API를 이용해 감정 분석 점수 계산
                        sentiment_score = get_sentiment(description_cleaned)

                        # PostgreSQL에 데이터 삽입
                        insert_news_data(conn, title_cleaned, description_cleaned, pubDate_cleaned, sentiment_score)
                    




                # 연결 종료
    except Exception as e:
        logging.error(f'Postgres 작업 중 오류 발생: {e}') 

    finally:
        if conn and not conn.closed:
            conn.close()


if __name__ == "__main__":
    main()
    new_data = fetch_new_data_from_postgres()  # PostgreSQL에서 데이터 가져오기
    if new_data:
        insert_data_to_redshift(new_data)  # Redshift로 데이터 삽입
        logging.info("Redshift로 데이터 이동 완료.")
    else:
        logging.info("PostgreSQL에서 가져올 새로운 데이터가 없습니다.")
