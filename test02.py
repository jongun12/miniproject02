import streamlit as st
import pandas as pd # 차트 그리기용

# [추가] 우리가 만든 모듈 가져오기
from test_naver_news import get_news_titles, get_news_data
from test_AI_API2 import analyze_sentiment_batch, analyze_news_batch

st.set_page_config(page_title="AI 뉴스 인사이트", layout="wide")

st.title("📰 AI 뉴스 인사이트")
keyword = st.text_input("검색어", "인공지능")

if st.button("분석 시작"):
    
    # -------------------------------------------------------
    # TRACK 1: 통계 분석 (제목 20개) - 빠름!
    # -------------------------------------------------------
    with st.spinner("1단계: 전체적인 여론을 분석 중입니다... (제목 20개)"):
        # 1. 제목만 가져오기
        titles = get_news_titles(keyword, limit=20)
        
        if not titles:
            st.error("뉴스를 찾을 수 없습니다.")
        else:
            # 2. AI로 감성 분석
            sentiment_result = analyze_sentiment_batch(titles, keyword=keyword)
            
            # 3. 결과 시각화 (막대 차트)
            st.subheader(f"📊 '{keyword}' 관련 여론 분석 (20건 기준)")
            
            # 데이터프레임 만들기
            df = pd.DataFrame({
                "감성": ["긍정", "중립", "부정"],
                "기사 수": [
                    sentiment_result["positive"], 
                    sentiment_result["neutral"], 
                    sentiment_result["negative"]
                ]
            })
            
            # Streamlit 내장 차트로 색상 지정해서 그리기
            st.bar_chart(
                df.set_index("감성"),
                color=["#4CAF50"] # 초록색 계열 (단색 예시, 커스텀 가능)
            )
            
            # 간단한 멘트 출력
            if not df.empty and df["기사 수"].sum() > 0:
                top_sentiment = df.sort_values(by="기사 수", ascending=False).iloc[0]["감성"]
                st.info(f"분석 결과, 현재 **{top_sentiment}적인 여론**이 가장 우세합니다.")

    st.markdown("---")

    # -------------------------------------------------------
    # TRACK 2: 상세 요약 (본문 3개) - 조금 느림
    # -------------------------------------------------------
    with st.spinner("2단계: 주요 뉴스 3개를 상세 분석 중입니다..."):
        # 1. 본문까지 포함된 뉴스 데이터 가져오기 (3개만)
        full_news = get_news_data(keyword, display_count=3)
        
        if full_news:
             # 2. AI에게 요약 및 분석 요청
            analyzed_list = analyze_news_batch(full_news, keyword=keyword)
            
            st.subheader("📝 주요 뉴스 상세 리포트")
            
            for news in analyzed_list:
                # 점수에 따른 이모지 표시
                score = news.get("score", 0)
                emoji = "😐"
                if score > 0.3: emoji = "😊"
                elif score < -0.3: emoji = "😡"
                
                with st.expander(f"{emoji} {news.get('title', '제목 없음')} ({news.get('sentiment', '중립')})"):
                    st.write(f"**요약:** {news.get('summary', '요약 없음')}")
                    st.caption(f"감성 점수: {score}")
                    
            st.success("✅ 모든 분석이 완료되었습니다!")
        else:
            st.warning("상세 분석을 위한 뉴스를 수집하지 못했습니다.")