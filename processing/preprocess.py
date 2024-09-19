import re
from datetime import datetime
import logging

# HTML 태그와 특수문자 제거 함수
def clean_html(raw_html):
    cleantext = re.sub(r'<.*?>', '', raw_html)  # 모든 HTML 태그 제거
    cleantext = re.sub(r'&quot;', '"', cleantext)  # &quot;를 큰따옴표로 변환
    return cleantext.strip()  # 양쪽 공백 제거

# 날짜 형식 변환 함수
def convert_date(date_string):
    try:
        return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.error(f'날짜 변환 실패: {e} (입력값: {date_string})')
        return date_string  # 변환에 실패하면 원래 날짜를 그대로 반환