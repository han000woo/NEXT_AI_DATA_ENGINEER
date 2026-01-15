
import streamlit as st

from utils import crud


st.set_page_config(page_title="상품 목록", page_icon="🛒", layout="wide")

st.title("🛒 상품 목록")

# API에서 상품 가져오기
products = crud.get_products()

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
                
                # 주문 버튼 (Key 중복 방지를 위해 ID 사용)
                if st.button("구매하기", key=f"buy_{p['id']}"):
                    if crud.create_order(p['id'], 1):
                        st.success(f"✅ {p['name']} 주문이 완료되었습니다!")
                        st.balloons()
                    else:
                        st.error("❌ 주문 실패: 서버 오류")
else:
    st.warning("등록된 상품이 없습니다. Admin 메뉴에서 상품을 등록해주세요.")