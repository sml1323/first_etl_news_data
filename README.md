# 뉴스 감정 분석 ETL 파이프라인
이 프로젝트는 네이버 뉴스 API를 통해 정치 뉴스 기사를 수집하고, OpenAI의 GPT 모델을 이용하여 감정 분석을 수행한 뒤, 데이터를 PostgreSQL과 Amazon Redshift에 적재하는 ETL 파이프라인입니다.


## 주요기능

- **뉴스 데이터 수집**: 네이버 뉴스 API를 사용하여 최신 정치 뉴스를 수집
- **데이터 전처리**: HTML 태그 제거 및 날짜 형식 변환 수행
- **감정 분석**: OpenAI GPT API를 사용하여 뉴스 기사에 대한 긍정-부정 점수 계산
- **데이터 저장**: 처리된 데이터를 PostgreSQL에 저장 후 Redshift로 전송

## 기술 스택

- **프로그래밍 언어**: Python 3.x
- **데이터베이스**: PostgreSQL, Amazon Redshift
- **API**: OpenAI GPT API, 네이버 뉴스 검색 API
- **패키지 및 라이브러리**: `psycopg2`, `openai`, `python-dotenv`, `redshift-connector`, `matplotlib`, `pandas`


## 설치 및 실행 방법

```bash
git clone

env에 변수 입력

## main.py 설정

fetch_limit  : 페이지 갯수
display      : 페이지당 가져올 뉴스의 수
start =      : 가져올 뉴스의 시작 페이지


   




