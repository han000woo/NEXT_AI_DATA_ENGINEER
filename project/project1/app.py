import streamlit as st
import graphviz

# 페이지 설정
st.set_page_config(page_title="AI Multiverse Counsel", page_icon="🌌", layout="wide")

def home_dashboard():
    """
    메인 페이지 
    """

    st.markdown(
        f"""
        <div style='text-align: center; padding-top: 20px; padding-bottom: 20px;'>
            <h1 style='font-size: 3rem; margin-bottom: 0;'>같은 질문, 다른 지혜</h1>
            <p style='font-size: 1.2rem; color: gray;'>
                "누구의 관점으로 답을 듣고 싶으신가요?"<br>
                오늘 당신의 고민을 들어줄 멘토를 선택하세요.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    

    st.header("Data Flow Diagram (DFD)")
    st.info("데이터 수집부터 서비스 제공까지의 흐름도")
    # Graphviz를 이용한 DFD 시각화
    dfd_graph = graphviz.Digraph()
    dfd_graph.attr(rankdir='LR')
    
    dfd_graph.node('DAS', 'DAS\n(Data Acquisition)\nCrawling', shape='box', style='filled', fillcolor='#e1f5fe')
    dfd_graph.node('DSS', 'DSS\n(Data Store)\nSQL / Vector DB', shape='cylinder', style='filled', fillcolor='#fff9c4')
    dfd_graph.node('JPS', 'JPS\n(Job Processing)\nJava / Python Logic', shape='component', style='filled', fillcolor='#ffe0b2')
    dfd_graph.node('WSS', 'WSS\n(Web Service)\nHTML / Streamlit', shape='tab', style='filled', fillcolor='#dcedc8')
    dfd_graph.edge('DAS', 'DSS', label='Raw Data')
    dfd_graph.edge('DSS', 'JPS', label='Query / RAG')
    dfd_graph.edge('JPS', 'WSS', label='Response')
    
    st.graphviz_chart(dfd_graph)

    # 탭을 사용하여 정보 구조화
    tab1, tab2, tab3, tab4 = st.tabs(["🏗️ 시스템 아키텍처", "⚙️ 개발 환경", "🚀 로드맵 & 이슈", "🧠 답변 로직 개선"])

    # 1. 시스템 아키텍처 & DFD
    # ---------------------------------------------------------
    with tab1:
        
        st.markdown("---")
        st.subheader("시스템 구성 요소")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            * **DAS (Data Acquisition System)**: 웹 크롤링 및 데이터 수집
            * **DSS (Data Store System)**: SQL 및 Vector DB 저장소
            """)
        with col2:
            st.markdown("""
            * **JPS (Job Processing System)**: Java/Python 백엔드 로직 처리
            * **WSS (Web Service System)**: HTML/Streamlit 프론트엔드
            """)

    # 2. 개발 환경 및 라이브러리
    # ---------------------------------------------------------
    with tab2:
        st.header("📦 라이브러리 및 환경 설정")
        st.warning("프로젝트 실행을 위해 아래 패키지 설치가 필요합니다.")

        st.code("""
# 기본 데이터 및 웹 프레임워크
pip install pandas
pip install streamlit
pip install streamlit_folium
pip install folium

# 문서 처리 (PDF, HWP)
pip install pymupdf  # PDF 처리
pip install olefile  # HWP 레거시 처리
pip install hwp5     # HWP 변환
        """, language="bash")

        st.subheader("📂 데이터 처리 전략")
        st.markdown("""
        * **Vector DB 저장 전략**: (To-Do) 텍스트 청킹(Chunking) 후 임베딩 저장 방식 결정 필요
        * **Template**: Streamlit Component 활용 예정
        """)

    # 3. 현재 진행 상황 및 이슈 (Roadmap)
    # ---------------------------------------------------------
    with tab3:
        st.header("🚧 진행 상황 및 애로사항")
        
        col_todo, col_issue = st.columns(2)
        
        with col_todo:
            st.markdown("### ✅ 구현 기능")
            st.checkbox("질문에 답변하는 기본 형식", value=True, disabled=True)
            st.checkbox("기독교(목사님) 데이터 확보 (TXT)", value=True, disabled=True)
            
            st.markdown("### 🗓️ 예정 기능")
            st.checkbox("두 챗봇 간의 대화 (토론 모드)")
            st.checkbox("Vector DB 구축")
        
        with col_issue:
            st.markdown("### ⚠️ 애로사항 (Issues)")
            st.error("불교(법륜스님) 데이터 확보 문제")
            st.caption("현재 영상 데이터만 존재함. Audio -> Text (STT) 변환 작업 필요.")
            
            st.warning("데이터 파이프라인")
            st.caption("PDF/HWP -> 텍스트 추출 정규화 과정 필요")

    # 4. 답변 로직 개선 (User Feedback 반영)
    # ---------------------------------------------------------
    with tab4:
        st.header("🧠 AI 페르소나 튜닝 방향")
        st.markdown("현재 AI가 **'성급하게 답을 주는 문제'**가 식별됨.")
        
        with st.container(border=True):
            st.markdown("### 🔄 개선된 대화 흐름 (Chain of Thought)")
            st.markdown("""
            1. **Active Listening (경청)**: 사용자의 상황이 모호하면 **되물어보기**
            2. **Empathy (공감)**: 답을 주기 전, 감정에 먼저 공감하기
            3. **Solution (조언)**: 상황을 파악한 후, 해당 페르소나의 관점으로 답변
            """)
            
        st.markdown("**예시 프롬프트 전략:**")
        st.code("""
"사용자가 '힘들다'고 했을 때, 
바로 성경 구절이나 법문을 제시하지 마십시오.
먼저 '어떤 일로 마음이 무거우신가요?'라고 구체적인 상황을 물어보세요.
충분한 맥락이 파악된 후에 조언을 건네세요."
        """, language="text")


# 1. 로그인/로그아웃/홈 (내부 함수 연결)
# login_page = st.Page(login_screen, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout_screen, title="Log out", icon=":material/logout:")
home_page = st.Page(home_dashboard, title="Home", icon=":material/home:", default=True)


pastor_jung = st.Page(
    "pages/PastorJung.py",
    title="정운성 목사님",
    icon=":material/volunteer_activism:",
)
pastor_kim = st.Page(
    "pages/PastorKim.py",
    title="김유진 목사님",
    icon=":material/volunteer_activism:",
)
Nietzsche = st.Page(
    "pages/Nietzsche.py",
    title="Nietzsche",
    icon=":material/psychology:",
)
Bubryune = st.Page(
    "pages/Bubryune.py",
    title="Bubryune",
    icon=":material/temple_buddhist:",
)
Arena = st.Page(
    "pages/Arena.py",
    title="Arena",
    icon=":material/sports_martial_arts:",
)


# is_logged_in = st.user.get("is_logged_in", False)

# if is_logged_in:
#     # [로그인 후]: 메인 대시보드와 각 메뉴 접근 가능
#     pg = st.navigation(
#     {
#         # "Account": [logout_page],
#         "Christian": [pastor_jung, pastor_kim],
#         "Buddhism": [Bubryune],
#         "Philosophy": [Nietzsche],
#         "Contents": [Arena],
#     }
#     )
# else:
#     # [로그인 전]: 로그인 화면만 접근 가능
#     pg = st.navigation([login_page])

pg = st.navigation(
    {
        "Home": [home_page],
        "Christian": [pastor_jung, pastor_kim],
        "Buddhism": [Bubryune],
        "Philosophy": [Nietzsche],
        "Contents": [Arena],
    }
)

pg.run()
