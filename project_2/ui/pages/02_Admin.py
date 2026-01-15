import streamlit as st
from utils import crud


st.set_page_config(page_title="관리자 페이지", page_icon="🔧", layout="wide")

st.title("🔧 상품 등록 (관리자)")

with st.container(border=True):
    st.header("새 상품 정보 입력")
    
    with st.form("product_form", clear_on_submit=True):
        name = st.text_input("상품명", placeholder="예: 멋진 티셔츠")
        desc = st.text_area("상품 설명", placeholder="상품에 대한 상세 설명을 적어주세요.")
        price = st.number_input("가격", min_value=0.0, step=1000.0, format="%.0f")
        img_url = st.text_input("이미지 URL", placeholder="https://example.com/image.jpg")
        
        submitted = st.form_submit_button("상품 등록하기")
        
        if submitted:
            if not name or price <= 0:
                st.error("상품명과 가격을 올바르게 입력해주세요.")
            else:
                data = {
                    "name": name,
                    "description": desc,
                    "price": price,
                    "image_url": img_url if img_url else None
                }
                
                if crud.create_product(data):
                    st.success("🎉 상품이 성공적으로 등록되었습니다!")
                else:
                    st.error("❌ 등록 실패: API 서버를 확인해주세요.")