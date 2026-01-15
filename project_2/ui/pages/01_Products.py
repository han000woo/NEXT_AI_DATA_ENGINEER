
import streamlit as st

from services import get_api


st.set_page_config(page_title="상품 목록", page_icon="🛒", layout="wide")

api = get_api()

st.title("🛒 상품 목록")

# 세션 초기화 
if 'cart' not in st.session_state:
    st.session_state['cart'] = [] 

# API에서 상품 가져오기
products = api.product.get_list()

if products:
    cols = st.columns(3)
    for idx, p in enumerate(products):
        with cols[idx % 3]:
            with st.container(border=True):
                # 이미지가 없으면 기본 이미지 사용
                img = p['image_url'] if p.get('image_url') else "https://via.placeholder.com/150"
                
                st.image(img, use_container_width=True)
                st.subheader(p['name'])
                
                # 긴 설명은 잘라서 보여주기
                desc = p['description']
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                st.write(desc)
                
                st.write(f"**💰 가격: ${p['price']}**")
                qty = st.number_input("수량", min_value=1, max_value=100, value=1, key=f"qty_{p['id']}")
                
                # 주문 버튼 (Key 중복 방지를 위해 ID 사용)
                if st.button("장바구니 담기", key=f"add_{p['id']}"):
                    item = {
                        "product_id" : p['id'],
                        "name" : p['name'],
                        "price" : p['price'],
                        "quantity" : qty
                    }
                    st.session_state['cart'].append(item)
                    st.toast(f"✅ {p['name']} {qty}개가 장바구니에 담겼습니다!")
else:
    st.warning("등록된 상품이 없습니다. Admin 메뉴에서 상품을 등록해주세요.")