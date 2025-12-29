import streamlit as st

st.header("가상환경 구축")

st.info(
    """
프로젝트의 의존성(라이브러리 버전 등)을 격리하여 관리하기 위해 가상환경을 사용합니다.
**Python 3.10 이상** 버전을 권장합니다.
"""
)

# OS별 명령어 분리

requirements_txt = """
----------------------------------------------------------------------------------------------
# Streamlit 웹 서버 

streamlit                # 파이썬으로 웹 UI를 빠르게 만들기 위한 프레임워크 (챗봇, 대시보드 등)
openai                   # OpenAI API 호출용 공식 SDK (GPT, 임베딩, 이미지 생성 등)
langchain-openai         # LangChain에서 OpenAI 모델(GPT, Embedding)을 쉽게 사용하기 위한 연동 패키지
langchain-chroma         # Chroma 벡터 DB를 LangChain과 함께 사용하기 위한 패키지 (RAG용 벡터 저장소)
langchain-core           # LangChain의 핵심 인터페이스와 기본 추상 클래스
langchain-text-splitters # 긴 문서를 청크(chunk) 단위로 분할하기 위한 도구 (RAG 전처리)
langchain-community      # 커뮤니티에서 제공하는 Loader, Tool, Retriever 등 확장 기능 모음
python-dotenv             # .env 파일에서 환경변수(API KEY 등)를 로드하기 위한 라이브러리

### 유튜브 데이터 크롤링 
youtube-transcript-api
yt-dlp

### hwp 파일 파싱 
olefile

### PDF 파일 파싱 
PyMuPDF
pysqlite3-binary

### MCP Client
mcp

----------------------------------------------------------------------------------------------
# MCP 서버 
mcp
feedparser
uvicorn
 """

os_tab1, os_tab2 = st.tabs(["Windows", "macOS / Linux"])

with os_tab1:
    st.subheader("Windows 설정 방법")
    st.write("1️⃣ **가상환경 생성** (터미널에서 프로젝트 루트 경로로 이동 후 입력)")
    st.code("python -m venv venv", language="powershell")

    st.write("2️⃣ **가상환경 활성화**")
    st.code(".\\venv\\Scripts\\activate", language="powershell")
    st.info("명령 프롬프트(cmd)를 쓰는 경우: `venv\\Scripts\\activate.bat`")
    st.write("3️⃣ **라이브러리 설치**")
    st.code("pip install -r requirements.txt", language="powershell")

    st.write("4️⃣ **requirements.txt**")
    st.code(requirements_txt)
with os_tab2:
    st.subheader("macOS / Linux 설정 방법")
    st.write("1️⃣ **가상환경 생성**")
    st.code("python3 -m venv venv", language="bash")

    st.write("2️⃣ **가상환경 활성화**")
    st.code("source venv/bin/activate", language="bash")
    st.write("3️⃣ **라이브러리 설치**")
    st.code("pip install -r requirements.txt", language="bash")
    st.write("4️⃣ **requirements.txt**")
    st.code(requirements_txt)
st.divider()
st.warning("**참고:** 가상환경을 비활성화하려면 터미널에 `deactivate`를 입력하세요.")
