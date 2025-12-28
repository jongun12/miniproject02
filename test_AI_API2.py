import json
import openai
import streamlit as st
import os

# 1. 뉴스 데이터 준비 (예시: 이미 크롤링 된 리스트)
news_list = [
    {"id": 1, "title": "AI 반도체 시장 급성장", "content": "엔비디아 주가가 폭등하며... (매우 긴 본문)"},
    {"id": 2, "title": "AI 저작권 소송 패소", "content": "예술가들이 제기한 소송에서... (매우 긴 본문)"},
    {"id": 3, "title": "정부, AI 예산 삭감 논란", "content": "내년도 R&D 예산이 줄어들며... (매우 긴 본문)"}
]

# API 키 설정
# Streamlit Cloud나 로컬 실행 환경(secrets.toml)에 따라 유연하게 처리
try:
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        api_key = os.getenv("OPENAI_API_KEY")
except FileNotFoundError:
    api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

def analyze_news_batch(news_items, output_limit=None):
    """
    뉴스 리스트를 통째로 받아서 한 번에 분석하는 함수
    :param news_items: 뉴스 데이터 리스트
    :param output_limit: 결과로 반환할 최대 개수 (기본값: None = 제한 없음)
    """
    if not api_key:
        print("API Key가 없습니다.")
        return []

    # [최적화 1] AI에게 보낼 데이터 경량화 (본문 1000자 제한) & ID 부여
    simplified_data = []
    id_map = {} # 결과 병합을 위한 맵
    
    for idx, news in enumerate(news_items):
        # ID가 없으면 인덱스로 부여
        news_id = news.get("id", idx)
        id_map[news_id] = news
        
        simplified_data.append({
            "id": news_id,
            "title": news["title"],
            "content": news["content"][:1000] # 앞부분 1000자만 자르기!
        })

    # [최적화 2] 시스템 프롬프트 수정
    # [주의] response_format={"type": "json_object"}를 쓸 때는 
    # 루트 요소가 반드시 JSON Object({})여야 합니다. List([])로 시작하면 오류가 발생할 수 있습니다.
    system_prompt = """
    너는 뉴스 분석 AI야. 입력된 뉴스 리스트를 분석해서 아래 JSON 형식으로 반환해.
    다른 말은 하지 말고 오직 JSON 데이터만 출력해.
    
    [응답 형식]
    {
        "articles": [
            {
                "id": 숫자,
                "summary": "핵심 내용 3줄 요약",
                "sentiment": "긍정" 또는 "부정" 또는 "중립",
                "score": -1.0 ~ 1.0 사이의 점수 (부정은 음수, 긍정은 양수)
            }
        ]
    }
    """

    user_prompt = json.dumps(simplified_data, ensure_ascii=False)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} # JSON 모드 강제
        )
        
        # 문자열로 온 응답을 다시 파이썬 객체로 변환
        content = response.choices[0].message.content
        result_json = json.loads(content)
        
        # [수정] 딕셔너리 안의 'articles' 리스트를 반환하도록 변경
        ai_results = result_json.get('articles', [])
        
        # [병합] AI 결과에 원본 데이터(제목, 링크 등) 합치기
        final_results = []
        for item in ai_results:
            item_id = item.get("id")
            original = id_map.get(item_id)
            if original:
                # 원본의 제목, 링크 등을 AI 결과에 덮어쓰기 (없으면 유지)
                item["title"] = original.get("title", item.get("title"))
                item["link"] = original.get("link")
                item["date"] = original.get("date")
                final_results.append(item)
        
        # [추가] 개수 제한 적용
        if output_limit and isinstance(output_limit, int):
            return final_results[:output_limit]
        
        return final_results

    except Exception as e:
        print(f"AI 호출 에러: {e}")
        return []

def analyze_sentiment_batch(titles):
    """
    뉴스 제목 리스트(10~20개)를 받아 긍정/부정/중립 개수와 점수를 반환
    """
    if not titles:
        return {"positive": 0, "negative": 0, "neutral": 0, "details": []}

    # 1. 프롬프트 작성 (JSON 포맷 강제)
    system_prompt = """
    너는 뉴스 감성 분석가야. 
    제공된 뉴스 제목들의 리스트를 보고 각각의 감성을 'positive', 'negative', 'neutral' 중 하나로 분류해.
    
    [중요] 'sentiment' 필드 값은 반드시 영어 소문자('positive', 'negative', 'neutral')로만 출력해야 해. 한글(긍정, 부정)은 절대 사용하지 마.
    
    반드시 아래 JSON 형식으로만 응답해 (다른 말 금지):
    {
        "results": [
            {"title": "뉴스 제목1", "sentiment": "positive"},
            {"title": "뉴스 제목2", "sentiment": "negative"}
        ]
    }
    """
    
    # 제목 리스트를 문자열로 변환해서 보냄
    user_content = json.dumps(titles, ensure_ascii=False)

    try:
        # 2. AI 호출 (gpt-4o-mini 추천: 싸고 빠름)
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 또는 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"} # JSON 모드 활성화
        )
        
        # 3. 응답 파싱
        data = json.loads(response.choices[0].message.content)
        results = data.get("results", [])
        
        # 4. 통계 계산 (카운팅)
        stats = {"positive": 0, "negative": 0, "neutral": 0, "details": results}
        for item in results:
            sentiment = item.get("sentiment", "neutral").lower()
            if sentiment in stats:
                stats[sentiment] += 1
                
        return stats

    except Exception as e:
        print(f"AI 분석 에러: {e}")
        return {"positive": 0, "negative": 0, "neutral": 0, "details": []}

# --- 실행 예시 ---
if __name__ == "__main__":
    results = analyze_news_batch(news_list)
    print(json.dumps(results, indent=2, ensure_ascii=False))