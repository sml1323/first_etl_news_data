# 뉴스 감정 분석 ETL 파이프라인
이 프로젝트는 네이버 뉴스 API를 통해 정치 뉴스 기사를 수집하고, OpenAI의 GPT 모델을 이용하여 감정 분석을 수행한 뒤, 데이터를 PostgreSQL과 Amazon Redshift에 적재하는 ETL 파이프라인입니다.

## 기술 스택

- Python 3.x
- PostgreSQL
- Amazon Redshift
- OpenAI GPT API
- 네이버 뉴스 검색 API

## 설치 및 실행 방법


1. **저장소 클론**

   ```bash
   git clone
   

   fetch_limit = 100 : 페이지 갯수
   display = 1       : 페이지당 가져올 뉴스의 수
   start = 1         : 가져올 뉴스의 시작 페이지




