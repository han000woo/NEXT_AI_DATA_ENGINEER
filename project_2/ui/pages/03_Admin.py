import streamlit as st
import pandas as pd
import time
from constants import PRODUCT_CATEGORIES # 상수 임포트
from services import get_api

api = get_api()

st.set_page_config(page_title="Admin Dashboard", page_icon="🔧", layout="wide")

st.title("Admin Dashboard")
st.markdown("---")

# 탭을 사용하여 기능 분리
tab1, tab2 = st.tabs(["New Product", "Edit / Delete"])

# ==========================================
# TAB 1: 상품 등록 (기존 코드 개선)
# ==========================================
with tab1:
    st.subheader("Register New Product")
    
    with st.container(border=True):
        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("Product Name", placeholder="Ex: Premium T-Shirt")
            desc = st.text_area("Description", placeholder="Enter product details...")
            
            c1, c2 = st.columns(2)
            with c1:
                price = st.number_input("Price", min_value=0.0, step=100.0, format="%.0f")
            with c2:
                img_url = st.text_input("Image URL", placeholder="https://...")
            
            submitted = st.form_submit_button("Register Product", type="primary")
            
            if submitted:
                if not name or price <= 0:
                    st.error("Please check the product name and price.")
                else:
                    data = {
                        "name": name, 
                        "description": desc, 
                        "price": price, 
                        "image_url": img_url if img_url else None
                    }
                    if api.product.create(data):
                        st.success("Product registered successfully!")
                        time.sleep(1)
                        st.rerun() # 목록 갱신을 위해 리로드
                    else:
                        st.error("Failed to register product.")

# ==========================================
# TAB 2: 상품 수정 및 삭제
# ==========================================
with tab2:
    st.subheader("Manage Products")
    
    # 1. 수정할 상품 선택하기
    products = api.product.get_list()
    
    if not products:
        st.info("No products found to edit.")
    else:
        # Selectbox에 표시될 이름을 만들기 위한 dict 생성
        product_options = {f"{p['id']}: {p['name']}": p for p in products}
        
        selected_option = st.selectbox(
            "Select a product to edit", 
            options=list(product_options.keys())
        )
        
        # 선택된 상품 데이터 가져오기
        target_product = product_options[selected_option]
        
        st.divider()
        
        # 2. 수정 폼 (기존 데이터로 채워진 상태)
        with st.container(border=True):
            st.markdown(f"**Editing: {target_product['name']}**")
            
            # 수정 폼의 Key는 유니크해야 함 (product_id 활용)
            with st.form(key=f"edit_form_{target_product['id']}"):
                new_name = st.text_input("Product Name", value=target_product['name'])
                new_desc = st.text_area("Description", value=target_product['description'] or "")
                
                c1, c2 ,c3 = st.columns(3)
                with c1:
                    new_price = st.number_input("Price", min_value=0.0, step=100.0, 
                                              value=float(target_product['price']), format="%.0f")
                with c2:
                    new_img_url = st.text_input("Image URL", value=target_product['image_url'] or "")

                with c3: 
                    try:
                        default_index = PRODUCT_CATEGORIES.index(target_product['category'])
                    except ValueError:
                        default_index = 0

                    new_category = st.selectbox(
                        "Select a category to edit",
                        options=list(PRODUCT_CATEGORIES),
                        index=default_index
                    )
                
                
                # 버튼 레이아웃: 수정(Blue) / 삭제(Red)
                col_update, col_delete = st.columns([4, 1])
                
                with col_update:
                    update_submitted = st.form_submit_button("Update Product", type="primary", use_container_width=True)
                
                # 삭제 기능은 Form 안에 넣으면 헷갈릴 수 있어 form 외부 혹은 별도 처리하지만,
                # 여기서는 폼 제출 버튼과 구분을 위해 아래에서 처리
                
                if update_submitted:
                    update_data = {
                        "name": new_name,
                        "description": new_desc,
                        "price": new_price,
                        "category" : new_category,
                        "image_url": new_img_url if new_img_url else None
                    }
                    if api.product.update(target_product['id'], update_data):
                        st.success("Product updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to update.")

            # 3. 삭제 구역 (안전하게 분리)
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            with st.expander("🗑️ Delete Product (Danger Zone)"):
                st.warning(f"Are you sure you want to delete '{target_product['name']}'?")
                if st.button("Yes, Delete Forever", type="primary"): # primary type이지만 빨간색 스타일링은 아님 (Streamlit 기본 제약)
                    if api.product.delete(target_product['id']):
                        st.success("Product deleted.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete.")