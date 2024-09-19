import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import urllib.request
import openai
import logging
load_dotenv()



def fetch_news_data(client_id, client_secret, encText, start=1, display=10):
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={display}&start={start}"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            news_data = json.loads(response_body.decode('utf-8'))['items']
            logging.info(f'가져온 뉴스 데이터: {news_data}')
            return news_data
        else:
            logging.warning(f"API 응답 코드: {rescode}, 데이터를 가져오지 못했습니다.")
            return []
    except Exception as e:
        logging.error(f"네이버 API 요청 중 오류 발생: {e}")
        return []

# 감정 분석 함수
def get_sentiment(text):
    # OpenAI API에 요청
    try:
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
        {
            "role": "user",
            "content": """
    다음은 한글 뉴스 기사에서 발췌한 문장입니다. 해당 문장의 감정을 -1에서 1 사이로 평가하세요. -1은 가장 부정적인 감정, 1은 가장 긍정적인 감정을 나타냅니다:

    박찬대 "순직 해병대원·김건희 특검법, 공정을 위한 법안", 그는 "군사독재 시절 정치군인이 차지한 자리를 정치 검사들이 꿰차며 '유검무죄 무검유죄'의 세상을 만들었다"고 주장했다. 또한, 현 정부가 야당을 국정운영의 파트너가 아닌 궤멸시킬 적으로 간주하고 있으며, 검찰이...
    """.strip(),
        },
        {"role": "assistant", "content": "-0.7"},
        {
            "role": "user",
            "content": """
    다음은 한글 뉴스 기사에서 발췌한 문장입니다. 해당 문장의 감정을 -1에서 1 사이로 평가하세요. -1은 가장 부정적인 감정, 1은 가장 긍정적인 감정을 나타냅니다:

    천하람 "野 특검법, 대법원장 가볍게 취급…삼권분립 안 맞아", 천 원내대표는 4일 SBS라디오 ‘김태현의 정치쇼’에 출연해 “대법원장은 말 그대로 사법부의 수장 아니냐”며 “사법부의 수장이 추천한 것에 대해 입법부의 일부인 야당이 비토를 하고 재추천을 해달라는 건 대법원장을...
    """.strip(),
        },
        {"role": "assistant", "content": "0.0"},
        {"role": "user",
                    "content": f"다음 문장의 감정을 -1에서 1 사이로 평가하세요: {text}"}],
            max_tokens=100,
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            stop=["\n"],
        )
        
        sentiment_score = float(response.choices[0].message.content)
        logging.info(f"감정 분석 결과: {sentiment_score}")
        return sentiment_score

    except openai.APIConnectionError as e:
        logging.error(f"OPENAI API 연결 중 오류발생: {e}")
        return None
    except openai.AuthenticationError as e:
        logging.error(f"OpenAI API 인증 오류: {e}")
        return None
    except openai.RateLimitError as e:
        logging.error(f"OpenAI 호출 제한 초과: {e}")
        return None
    except Exception as e:
        logging.error(f"감정분석중 알수 없는 오류 발생: {e}")
        return 0.0
    
    