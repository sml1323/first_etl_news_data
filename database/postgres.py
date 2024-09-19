import psycopg2
from datetime import datetime
import logging

def connect_postgres(db_host, db_user, db_password, db_name):
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=5432,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        return conn
    except Exception as e:
        print(f"Postgres 연결에 실패했습니다: {e}")
        return None

def insert_news_data(conn, title, description, pubdate, sentiment):
    try:
        with conn.cursor() as cur:
            insert_query = """
            INSERT INTO news_data (title, description, pubdate, sentiment)
            VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_query, (title, description, pubdate, sentiment))
            conn.commit()
            logging.info(f"데이터 삽입 성공: {title}, {pubdate}, {sentiment}")
    except Exception as e:
        logging.error(f"데이터 삽입 중 오류발생: {e} (title: {title}, description: {description}, pubdate: {pubdate}, sentiment: {sentiment})")
        conn.rollback()

def get_last_pubdate_from_db(conn):
    """PostgreSQL에서 가장 최근의 뉴스 pubDate를 가져옵니다."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(pubdate) FROM news_data")
            result = cur.fetchone()
            if result[0]:  # pubDate가 있을 때 처리
                # result[0]이 datetime 객체일 수 있으므로, 그에 맞게 처리
                if isinstance(result[0], datetime):
                    return result[0]
                else:
                    return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
            else:
                return None  # DB에 데이터가 없는 경우
    except Exception as e:
        print(f"Postgres에서 마지막 pubdate를 가져오는 중 오류 발생: {e}")
        return None
