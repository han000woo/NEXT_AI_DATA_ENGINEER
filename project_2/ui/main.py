import streamlit as st

st.set_page_config(
    page_title="My Shop Home",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 환영합니다! My Shop")

st.markdown("""
### 즐거운 쇼핑 되세요!
왼쪽 사이드바 메뉴를 통해 이동할 수 있습니다.

- **🛒 Products**: 상품을 구경하고 주문하세요.
- **🔧 Admin**: (관리자용) 새로운 상품을 등록하세요.
""")

st.info("👈 사이드바를 열어 메뉴를 선택해주세요.")