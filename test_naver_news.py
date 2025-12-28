import requests
from newspaper import Article
from datetime import datetime # [추가] 날짜 처리를 위한 도구
import streamlit as st
import os
import html

# ==========================================
# 설정 (본인의 키로 변경해주세요)
# ==========================================
try:
    client_id = st.secrets["NAVER_CLIENT_ID"]
    client_secret = st.secrets["NAVER_CLIENT_SECRET"]
except (FileNotFoundError, KeyError):
    # 로컬 환경 변수 또는 직접 입력 (비권장)
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")

def get_news_data(keyword, display_count=5):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": keyword,
        "display": display_count,
        "sort": "sim" # [변경] 최신 뉴스부터 보려면 'date', 관련도순은 'sim'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        items = response.json().get("items", [])
        
        news_list = []
        
        for item in items:
            # 1. 기본 정보 추출
            title = item['title'].replace('<b>', '').replace('</b>', '')
            link = item['originallink'] if item['originallink'] else item['link']
            
            # 2. 날짜 추출 및 변환 (포맷팅)
            # 네이버 원본 예시: "Fri, 26 Dec 2025 14:00:00 +0900"
            raw_date = item['pubDate'] 
            
            try:
                # 글자(str)를 날짜 객체(datetime)로 변환
                dt_object = datetime.strptime(raw_date, "%a, %d %b %Y %H:%M:%S %z")
                # 보기 좋게 다시 글자로 변환 (예: 2025-12-26 14:00)
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M")
            except Exception:
                formatted_date = raw_date # 변환 실패 시 원본 그대로 사용

            # 3. 본문 크롤링
            content = ""
            try:
                article = Article(link, language='ko')
                article.download()
                article.parse()
                content = article.text
            except:
                continue

            if len(content) > 50:
                news_list.append({
                    "title": title,
                    "link": link,
                    "date": formatted_date, # [추가] 변환된 날짜 저장
                    "content": content
                })
        
        return news_list

    except Exception as e:
        print(f"에러 발생: {e}")
        return []

def get_news_titles(keyword, limit=20):
    """
    네이버 API를 통해 '제목'과 '링크'만 빠르게 가져오는 함수
    (본문 크롤링 X -> 속도 매우 빠름)
    """
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": keyword,
        "display": limit,  # 요청한 개수만큼 가져옴 (예: 20개)
        "sort": "sim"      # 관련도순
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        items = response.json().get("items", [])
        
        simple_list = []
        for item in items:
            # HTML 태그 제거 및 엔티티 변환 (&quot; -> ", &lt; -> < 등)
            clean_title = html.unescape(item['title'].replace('<b>', '').replace('</b>', ''))
            simple_list.append(clean_title)
            
        return simple_list # 제목 문자열만 담긴 리스트 반환

    except Exception as e:
        print(f"Error: {e}")
        return []

# --- 테스트 ---
if __name__ == "__main__":
    results = get_news_data("인공지능", 5)
    for news in results:
        print(f"[{news['date']}] {news['title']}")
        print(f"[{news['link']}")
        print(f"[{len(news['content'])}자]{news['content'][:100]}...")
        print("-" * 50)