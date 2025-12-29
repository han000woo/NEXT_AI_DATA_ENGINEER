import streamlit as st 
import time

from utils.util import stream_data 

st.header("Streamlit 기본 사용법")

st.info("Streamlit은 데이터 스크립트를 웹 앱으로 빠르게 변환해주는 Python 라이브러리입니다.")

st.subheader("설치 및 실행")

st.code("pip install streamlit", language="bash")

st.code("streamlit run app.py", language="bash")


# ------------------------------------------------------------------
# Streamlit 매뉴얼 UI 구성
# ------------------------------------------------------------------
st.header("Streamlit 핵심 기능 매뉴얼")
st.caption("개발에 사용된 주요 명령어와 예제 코드입니다.")

# 카테고리별 탭 구분
tab_basic, tab_layout, tab_chat, tab_state, tab_deco, tab_nav = st.tabs([
    "기본 설정 & 텍스트", 
    "레이아웃 & 인터랙션", 
    "챗봇 전용 UI", 
    "상태 관리 (State)",
    "데코레이션",
    "페이지"
])

# 1. 기본 설정 & 텍스트 탭
with tab_basic:
    st.subheader("1. 페이지 설정 및 텍스트 출력")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("##### 코드 예시")
        st.code("""
# 1. 페이지 전체 설정 (코드 최상단 필수)
st.set_page_config(
    page_title="My App",
    page_icon="🦉",
    layout="wide"
)

# 2. 제목 및 구분선
st.title("메인 제목입니다")
st.divider() # 가로 구분선

# 3. 다양한 텍스트 출력
st.write("변수, 데이터프레임, 텍스트 등 만능 출력")
st.markdown("## 마크다운 문법 **강조** 가능")
st.caption("회색의 작은 설명 텍스트 (주석용)")

# 4. HTML 커스텀 (CSS 등)
st.html("<span style='color:blue'>HTML 적용</span>")
        """, language="python")
        
    with col2:
        st.markdown("##### 미리보기")
        with st.container(border=True):
            st.write("(`set_page_config`는 앱 실행 시 한 번만 적용됩니다)")
            st.title("메인 제목입니다")
            st.divider()
            st.write("write는 텍스트뿐만 아니라 리스트, dict도 출력합니다.")
            st.markdown("markdown은 **볼드체**, *이탤릭*, [링크](https://streamlit.io) 등을 지원합니다.")
            st.caption("이것이 caption입니다. 부가 설명에 좋습니다.")
            st.html("<div style='background:#e0f2fe; color:#0369a1; padding:5px; border-radius:5px;'>HTML로 스타일링된 박스입니다.</div>")

# 2. 레이아웃 & 인터랙션 탭
with tab_layout:
    st.subheader("2. 화면 구성 및 사용자 입력")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("##### 코드 예시")
        st.code("""
# 1. 내용을 접었다 폈다 하기
with st.expander("ℹ️ 자세한 내용 보기"):
    st.write("숨겨져 있던 내용입니다!")

# 2. 버튼 (클릭 시 True 반환)
if st.button("클릭해보세요", type="primary"):
    st.toast("버튼이 클릭되었습니다!")

# 3. 페이지 이동 링크
st.page_link("app.py", label="홈으로 가기", icon="🏠")
        """, language="python")

    with col2:
        st.markdown("##### 미리보기")
        with st.container(border=True):
            with st.expander("ℹ️ 자세한 내용 보기"):
                st.info("숨겨져 있던 내용입니다!")
            
            st.write("") # 간격
            
            if st.button("클릭해보세요", type="primary"):
                st.write("버튼이 클릭되었습니다!")
            
            st.write("")
            # 실제 파일이 없으면 에러가 날 수 있어 버튼처럼 보이게만 처리
            st.page_link("pages/Home.py", label="홈으로 가기", icon="🏠")
            

# 3. 챗봇 전용 UI 탭 (가장 중요!)
with tab_chat:
    st.subheader("3. 챗봇 개발 필수 기능")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("##### 코드 예시")
        st.code("""
# 1. 채팅 메시지 말풍선
with st.chat_message("user"):
    st.write("안녕, AI?")

with st.chat_message("assistant", avatar="🦉"):
    st.write("안녕하세요! 무엇을 도와드릴까요?")

# 2. 로딩 표시 (Spinner)
with st.spinner("생각하는 중..."):
    time.sleep(2) 
    st.write_stream(stream_data("이것은 답변 입니다. 저는 정말 친절한 챗봇입니다."))
    st.write_stream(stream_data("NEXT AI : 데이터 엔지니어링 모두들 화이팅입니다. "))

# 3. 스트리밍 출력 (타자기 효과)
# stream_data()는 제너레이터 함수여야 함
st.write_stream(stream_data)

# 4. 채팅 입력창
prompt = st.chat_input("질문을 입력하세요...")
if prompt:
    st.write(f"입력값: {prompt}")
        """, language="python")

    with col2:
        st.markdown("##### 미리보기")
        with st.container(border=True, height=400):
            # 채팅 말풍선
            with st.chat_message("user"):
                st.write("안녕, AI?")
            
            with st.chat_message("assistant", avatar="🦉"):
                st.write("안녕하세요! 무엇을 도와드릴까요?")
            
            # 스트리밍 버튼
            if st.button("스트리밍 테스트"):
                with st.spinner("답변 생성 중... (Spinner)"):
                    time.sleep(2) 
                st.write_stream(stream_data("이것은 답변 입니다. 저는 정말 친절한 챗봇입니다."))
                st.write_stream(stream_data("NEXT AI : 데이터 엔지니어링 모두들 화이팅입니다. "))

            # 입력창 (UI 하단 고정됨 - 미리보기에서는 비활성 느낌으로 설명)
            st.caption("아래 입력창이 `chat_input` 입니다.")
            st.chat_input("이곳에 메시지를 입력합니다 (데모)")

# 4. 상태 관리 탭
with tab_state:
    st.subheader("4. Session State (메모리)")
    st.markdown("Streamlit은 버튼을 누르면 코드가 처음부터 다시 실행됩니다. **변수를 기억하려면 `session_state`가 필수**입니다.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("##### 코드 예시")
        st.code("""
# 1. 초기화 (없으면 생성)
if "count" not in st.session_state:
    st.session_state.count = 0

# 2. 값 증가
def increment():
    st.session_state.count += 1

st.button("카운트 증가", on_click=increment)

# 3. 값 출력
st.write(f"현재 카운트: {st.session_state.count}")
        """, language="python")

    with col2:
        st.markdown("##### 미리보기")
        with st.container(border=True):
            # 실제 동작 구현
            if "manual_count" not in st.session_state:
                st.session_state.manual_count = 0
            
            def increment_manual():
                st.session_state.manual_count += 1
            
            st.write(f"현재 숫자: **{st.session_state.manual_count}**")
            
            st.button("➕ 숫자 올리기", on_click=increment_manual, key="demo_btn")
            
            if st.button("🔄 초기화"):
                st.session_state.manual_count = 0
                st.rerun()

with tab_deco:
    st.subheader("**5. Decorator (@st.cache_resource)**")
    st.markdown("""
    Streamlit은 버튼을 누를 때마다 코드를 처음부터 끝까지 다시 실행합니다. 
    **하지만, AI 모델을 로딩하거나 DB에 연결하는 무거운 작업을 매번 다시 한다면 앱이 매우 느려지겠죠?**
    
    이때 사용하는 것이 바로 **캐싱(Caching)** 데코레이터입니다.
    """)

    # 1. 개념 설명 및 코드 예시
    col1, col2 = st.columns([1, 1])
        
    with col1:
        st.markdown("##### 코드 예시")
        st.code("""
import time

# 이 함수는 최초 1회만 실행됩니다!
@st.cache_resource
def load_ai_model():
    time.sleep(3)  # 로딩에 3초 걸린다고 가정
    return "🧠 거대 AI 모델 로드 완료!"

st.write("모델 로딩 시작...")
model = load_ai_model() # 첫 실행: 3초 소요 / 이후: 0초
st.success(model)
        """, language="python")

    st.divider()

    # 2. 인터랙티브 데모 (실제 작동 확인)
    st.markdown("##### ⏱️ 성능 차이 체험하기")
    st.caption("아래 버튼을 눌러보세요. 첫 번째 클릭은 느리지만, 두 번째 클릭부터는 즉시 완료됩니다.")

    # 캐싱 함수 정의 (실제 데모용)
    @st.cache_resource
    def load_heavy_resource():
        time.sleep(2) # 2초 지연 시뮬레이션
        return "✅ 무거운 리소스(DB/Model) 로드 성공!"

    if st.button("무거운 작업 실행 (캐싱 적용됨)", key="cache_btn"):
        start_time = time.time()
        result = load_heavy_resource()
        end_time = time.time()
        
        duration = end_time - start_time
        
        st.success(result)
        if duration > 1.0:
            st.warning(f"🐢 첫 실행이라 오래 걸렸습니다: {duration:.2f}초")
        else:
            st.balloons()
            st.info(f"⚡ 캐시된 결과를 가져왔습니다! (엄청 빠름): {duration:.4f}초")

    with col2:
        st.markdown("##### st.cache_resource 란?")
        with st.container(border=True) :
            st.markdown("""
            - **용도:** DB 연결, 머신러닝 모델 로드 등 **'무겁고 변하지 않는 전역 객체'**를 저장할 때 사용합니다.
            - **특징:** 한 번 실행된 결과(객체)를 메모리에 저장해두고, 다음번 요청 때는 저장된 것을 바로 꺼내 씁니다.
            - **장점:** 앱 속도가 획기적으로 빨라집니다.
        """)

with tab_nav: # 새로운 탭 변수명 (예: tab_nav)
    st.subheader("6. 멀티 페이지 & 네비게이션 (v1.36+)")
    st.markdown("""
    Streamlit 1.36 버전부터 도입된 **최신 페이지 관리 방식**입니다.
    기존의 `pages` 폴더 방식보다 훨씬 유연하게 **메뉴 그룹핑, 아이콘 설정, 조건부 페이지 노출**이 가능합니다.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("##### 코드 구조 설명")
        st.code("""
import streamlit as st

# 1. 페이지 객체 정의 (st.Page)
# - 첫 번째 인자: 실행할 파일 경로 OR 함수명
# - title: 사이드바에 표시될 이름
# - icon: 구글 Material Icon 사용 가능
manual1 = st.Page("pages/mannual1.py", title="가상환경구축 메뉴얼", icon=":material/settings:")
manual2 = st.Page("pages/mannual2.py", title="Streamlit 메뉴얼", icon=":material/settings:")
manual3 = st.Page("pages/mannual3.py", title="Diagram", icon=":material/settings:")
                
# 2. 네비게이션 구조 정의 (st.navigation)
# - Dictionary를 사용하면 '섹션(그룹)'을 만들 수 있습니다.
pg = st.navigation({
    "Settings": [mannual1, mannual2, mannual3],
})

# 3. 페이지 실행 (필수!)
pg.run()
        """, language="python")

    with col2:
        st.markdown("##### 핵심포인트")
        with st.container(border=True):
            st.markdown("""
            **1. st.Page()**
            - 개별 페이지를 정의합니다.
            - `:material/icon_name:` 형식으로 깔끔한 아이콘을 넣을 수 있습니다.

            **2. st.navigation()**
            - 리스트(`[]`)로 넘기면 평이한 메뉴가 되고,
            - 딕셔너리(`{}`)로 넘기면 **'소제목(Section)'**이 있는 그룹 메뉴가 됩니다.

            **3. pg.run()**
            - 정의된 네비게이션 설정에 따라 **실제로 현재 페이지를 화면에 그려주는** 명령어입니다.
            - 이 코드는 **메인 진입 파일(app.py)**에만 있어야 합니다.
            """)
