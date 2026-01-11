import streamlit as st
import requests
import pandas as pd

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000/generate-logs"

st.set_page_config(page_title="DE Log Generator", layout="wide")

st.title("📊 DE Portfolio: Log Generator")
st.markdown("FastAPI 기반의 로그 생성기를 제어하는 대시보드입니다.")

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    count = st.number_input("생성할 로그 개수", min_value=1, max_value=1000, value=10)
    generate_btn = st.button("로그 생성하기")

# 메인 화면 로직
if generate_btn:
    with st.spinner("Backend 서버에 요청 중..."):
        try:
            # FastAPI로 POST 요청 전송
            response = requests.post(API_URL, json={"count": count})

            if response.status_code == 200:
                data = response.json()
                st.success(f"{len(data)}개의 로그가 생성되었습니다!")

                # JSON 데이터를 Pandas DataFrame으로 변환하여 표로 보여주기
                df = pd.DataFrame(data)

                st.subheader("📋 생성된 데이터 미리보기")
                st.dataframe(df, use_container_width=True)

                # JSON 원본 보기 (디버깅용)
                with st.expander("JSON 원본 데이터 확인"):
                    st.json(data)
            else:
                st.error(f"오류 발생: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ 서버에 연결할 수 없습니다. FastAPI 서버가 켜져 있는지 확인해주세요."
            )
