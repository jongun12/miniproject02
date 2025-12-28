import streamlit as st
import time

# 1. 페이지 기본 설정 (제목, 레이아웃)
st.set_page_config(
    page_title="AI 뉴스 인사이트",
    page_icon="📰",
    layout="wide"
)

# 2. 사이드바: 사용자 입력 공간
with st.sidebar:
    st.header("🔍 검색 옵션")
    keyword = st.text_input("키워드를 입력하세요", value="인공지능")

    
    if st.button("분석 시작 🚀"):
        st.session_state['searched'] = True
    else:
        st.session_state['searched'] = False

# 3. 메인 화면: 결과 대시보드
st.title("📰 AI 뉴스 요약 & 감성 분석 대시보드")
st.markdown("---")

# [추가] 모듈 가져오기
from news_crawler import get_news_titles, get_news_data
from ai_analyzer import analyze_sentiment_batch, analyze_news_batch
import pandas as pd

# [시나리오] 사용자가 버튼을 눌렀을 때만 결과를 보여줌
if st.session_state['searched']:
    
    # 3-1. 로딩 효과 (UX)
    with st.spinner(f"'{keyword}' 관련 뉴스를 수집하고 분석 중입니다..."):
        # (1) 트랙 1: 통계용 제목 수집 및 감성 분석
        titles = get_news_titles(keyword, limit=20)
        sentiment_result = analyze_sentiment_batch(titles, keyword=keyword)
        
        # (2) 트랙 2: 상세용 본문 수집 및 요약 (5건 수집 -> 3건 출력)
        full_news = get_news_data(keyword, display_count=5)
        analyzed_list = analyze_news_batch(full_news, output_limit=3, keyword=keyword)

    # 데이터 가공 (통계)
    total_count = len(titles)
    pos_count = sentiment_result.get("positive", 0)
    neg_count = sentiment_result.get("negative", 0)
    neu_count = sentiment_result.get("neutral", 0)
    
    # 긍정 비율 계산
    if total_count > 0:
        pos_ratio = int((pos_count / total_count) * 100)
    else:
        pos_ratio = 0
        
    # 대표 감성 선정
    sentiment_map = {"positive": "😊 긍정적", "negative": "😟 부정적", "neutral": "😐 중립적"}
    top_sentiment_key = max(sentiment_result, key=lambda k: sentiment_result[k] if k in ["positive", "negative", "neutral"] else -1)
    if total_count == 0: 
        top_sentiment_label = "데이터 없음"
    else:
        top_sentiment_label = sentiment_map.get(top_sentiment_key, "정보 없음")

    # 3-2. 핵심 지표 (Metrics) - 3단 컬럼
    col1, col2, col3 = st.columns(3)
    col1.metric(label="수집된 뉴스", value=f"{total_count} 건")
    col2.metric(label="긍정적 여론", value=f"{pos_ratio} %")
    col3.metric(label="대표 감성", value=top_sentiment_label)

    st.markdown("### 📊 감성 분석 리포트")
    
    # 3-3. 차트와 뉴스 리스트를 1:2 비율로 배치
    chart_col, news_col = st.columns([1, 2])
    
    with chart_col:
        st.info("뉴스 논조 분석 결과")
        # 막대 차트 데이터 구성
        chart_data = pd.DataFrame({
            "감성": ["긍정", "중립", "부정"],
            "기사 수": [pos_count, neu_count, neg_count]
        }).set_index("감성")
        
        st.bar_chart(chart_data, color=["#4CAF50"]) # 초록색 계열
        st.caption("검색된 뉴스 데이터 기반")

    with news_col:
        st.subheader("📝 주요 뉴스 요약")
        
        if not analyzed_list:
            st.warning("분석할 뉴스가 없습니다.")
        else:
            for news in analyzed_list:
                # 점수에 따른 이모지/라벨
                score = news.get("score", 0)
                sentiment_label = news.get("sentiment", "중립")
                
                emoji = "😐"
                if sentiment_label == "긍정" or score > 0.3: emoji = "✅"
                elif sentiment_label == "부정" or score < -0.3: emoji = "⚠️"
                
                # 익스팬더로 뉴스 표시
                with st.expander(f"{emoji} {news.get('title', '제목 없음')} ({sentiment_label})"):
                    st.write(f"**요약:** {news.get('summary', '요약 없음')}")
                    
                    # 점수 시각화 (선택 사항)
                    st.info(f"감성 점수: {score}")
                    
                    link = news.get('link', '#')
                    if link:
                        st.markdown(f"[원문 보기 >]({link})")

else:
    # 검색 전 초기 화면
    st.info("👈 왼쪽 사이드바에서 키워드를 입력하고 '분석 시작'을 눌러주세요.")
    st.markdown("""
    ### 이 앱은 무엇을 하나요?
    1. **뉴스 수집:** 입력한 키워드의 최신 뉴스를 가져옵니다.
    2. **AI 요약:** 바쁜 당신을 위해 3줄로 핵심만 요약합니다.
    3. **감성 분석:** 뉴스가 긍정적인지 부정적인지 판단해줍니다.
    """)