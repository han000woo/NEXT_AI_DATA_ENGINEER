import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="메인 페이지",
    page_icon="🏠",
    layout="wide"
)

st.sidebar.success("위의 메뉴에서 페이지를 선택하세요.")

st.title("🚀 메인 대시보드")
st.write("왼쪽 사이드바를 클릭하여 다른 페이지로 이동할 수 있습니다.")

# 메인 화면에 들어갈 내용
st.info("이것은 다중 페이지 앱의 메인 화면입니다.")