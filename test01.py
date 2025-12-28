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

# [시나리오] 사용자가 버튼을 눌렀을 때만 결과를 보여줌
if st.session_state['searched']:
    
    # 3-1. 로딩 효과 (UX)
    with st.spinner(f"'{keyword}' 관련 뉴스를 수집하고 분석 중입니다..."):
        time.sleep(1.5) # 분석하는 척 딜레이
    
    # 3-2. 핵심 지표 (Metrics) - 3단 컬럼
    col1, col2, col3 = st.columns(3)
    col1.metric(label="수집된 뉴스", value="15 건", delta="어제보다 +3")
    col2.metric(label="긍정적 여론", value="75 %", delta="상승세")
    col3.metric(label="대표 감성", value="😊 희망적")

    st.markdown("### 📊 감성 분석 리포트")
    
    # 3-3. 차트와 뉴스 리스트를 1:2 비율로 배치
    chart_col, news_col = st.columns([1, 2])
    
    with chart_col:
        st.info("뉴스 논조 분석 결과")
        # 간단한 막대 차트 예시 (긍정 vs 부정)
        st.bar_chart({"긍정": 75, "부정": 15, "중립": 10})
        st.caption("검색된 뉴스 데이터 기반")

    with news_col:
        st.subheader("📝 주요 뉴스 요약")
        
        # (더미 데이터 1: 긍정 뉴스)
        with st.expander("✅ [AI] 생성형 인공지능, 산업의 판도를 바꾼다 (긍정 0.9)"):
            st.write("**요약:** 생성형 AI 기술이 제조업과 서비스업 효율을 200% 이상 증대시켰습니다. 전문가들은 이를 '제4차 산업혁명의 완성'이라 평가합니다.")
            st.markdown("[원문 보기 >](https://naver.com)")
            
        # (더미 데이터 2: 부정 뉴스)
        with st.expander("⚠️ [우려] AI 저작권 분쟁, 해결책은 요원해 (부정 0.8)"):
            st.error("감성 분석 결과: 부정적 (Score: -0.8)")
            st.write("**요약:** 예술가들의 창작물이 AI 학습에 무단 사용되며 소송이 잇따르고 있습니다. 법적 규제 마련이 시급하다는 지적입니다.")
            st.markdown("[원문 보기 >](https://google.com)")

        # (더미 데이터 3: 중립 뉴스)
        with st.expander("ℹ️ [기술] 내년도 AI 예산안 국회 통과 (중립 0.1)"):
            st.write("**요약:** 정부의 내년도 AI 관련 연구개발 예산이 어제 국회를 통과했습니다. 전년 대비 소폭 상승한 규모입니다.")
            st.markdown("[원문 보기 >](https://daum.net)")

else:
    # 검색 전 초기 화면
    st.info("👈 왼쪽 사이드바에서 키워드를 입력하고 '분석 시작'을 눌러주세요.")
    st.markdown("""
    ### 이 앱은 무엇을 하나요?
    1. **뉴스 수집:** 입력한 키워드의 최신 뉴스를 가져옵니다.
    2. **AI 요약:** 바쁜 당신을 위해 3줄로 핵심만 요약합니다.
    3. **감성 분석:** 뉴스가 긍정적인지 부정적인지 판단해줍니다.
    """)