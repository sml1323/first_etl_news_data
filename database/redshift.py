import psycopg2
import redshift_connector
import logging
import os
from dotenv import load_dotenv
load_dotenv()
# PostgreSQL 관련 환경 변수
db_host = 'localhost'
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_name = os.getenv("db_name")

# redshift 환경변수
redshift_host = os.getenv('redshift_host')
redshift_user = os.getenv('redshift_user')
redshift_password = os.getenv("redshift_password")

# 문자열을 바이트 단위로 자르기 위한 함수
def truncate_bytes(text, max_bytes):
    encoded_text = text.encode('utf-8')
    if len(encoded_text) > max_bytes:
        truncated_text = encoded_text[:max_bytes]
        return truncated_text.decode('utf-8', errors='ignore')
    return text

# PostgreSQL에서 데이터 가져오기
def fetch_new_data_from_postgres():
    logging.info('Postgres -> Redshift 데이터 이동 준비')

    # PostgreSQL 연결
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    
    cur = conn.cursor()

    # Redshift에서 가장 최근의 pubDate 가져오기
    redshift_conn = redshift_connector.connect(
        host=redshift_host,
        port=5439,
        database='dev',
        user=redshift_user,
        password=redshift_password
    )
    
    redshift_cur = redshift_conn.cursor()
    redshift_cur.execute("SELECT MAX(pubDate) FROM news_data")
    last_pubdate = redshift_cur.fetchone()[0]

    logging.info(f'Redshift에서 가져온 마지막 pubdate: {last_pubdate}')

    # PostgreSQL에서 pubDate 기준으로 최신 데이터 가져오기
    if last_pubdate:
        query = "SELECT * FROM news_data WHERE pubDate > %s ORDER BY pubDate ASC"
        cur.execute(query, (last_pubdate,))
    else:
        query = "SELECT * FROM news_data ORDER BY pubDate ASC"
        cur.execute(query)

    new_data = cur.fetchall()
    cur.close()
    conn.close()
    
    return new_data

# Redshift에 데이터 삽입
def insert_data_to_redshift(new_data):
    if not new_data:
        logging.info("새로운 데이터가 없습니다.")
        return
    
    try:
        # Redshift 연결
        conn = redshift_connector.connect(
            host=redshift_host,
            database='dev',
            user=redshift_user,
            password=redshift_password
        )
        cur = conn.cursor()

        for record in new_data:
            # 각 필드를 바이트 제한에 맞게 자르기
            truncated_title = truncate_bytes(record[1], 255)  # title은 255바이트로 자름
            truncated_description = truncate_bytes(record[2], 256)  # description은 256바이트로 자름

            # Redshift에 데이터 삽입
            query = """
            INSERT INTO news_data (title, description, pubDate, sentiment)
            VALUES (%s, %s, %s, %s);
            """
            cur.execute(query, (truncated_title, truncated_description, record[3], float(record[4])))

        conn.commit()  # 트랜잭션 커밋
        logging.info(f"{len(new_data)}개의 데이터를 Redshift에 성공적으로 삽입했습니다.")
    
    except Exception as e:
        logging.error(f'Redshift에 데이터 삽입 중 오류 발생: {e}')
        conn.rollback()  # 오류 발생 시 롤백
        raise

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

