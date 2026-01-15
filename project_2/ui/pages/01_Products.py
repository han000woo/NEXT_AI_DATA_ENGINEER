import streamlit as st
from services import get_api

st.set_page_config(page_title="상품 목록", page_icon="🛒", layout="wide")

api = get_api()

st.title("🛒 상품 목록")

import streamlit as st

st.markdown(
    """
    <style>
    /* 탭 글씨 크기 조절 */
    div[data-baseweb="tab"] > button {
        font-size: 18px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# 1. 세션 초기화
if 'cart' not in st.session_state:
    st.session_state['cart'] = []

# 2. API에서 상품 가져오기
products = api.product.get_list()

if not products:
    st.warning("등록된 상품이 없습니다. Admin 메뉴에서 상품을 등록해주세요.")
    st.stop()

# 3. 카테고리 추출 (Set으로 중복제거 -> List로 변환 -> 정렬)
# 상품에 카테고리가 없으면 'Etc'로 처리
categories = sorted(list(set([p.get('category', 'Etc') for p in products])))

# 탭 이름 구성: 첫 번째는 '전체보기', 그 뒤로 카테고리들
tab_names = ["전체보기"] + categories
tabs = st.tabs(tab_names)

# ==========================================
# 🛠️ 헬퍼 함수: 상품 그리드 그리기
# ==========================================
def show_product_grid(product_list, tab_key):
    """
    product_list: 출력할 상품 리스트
    tab_key: 버튼 키 중복 방지를 위한 탭 식별자 (예: 'ALL', 'Electronics')
    """
    if not product_list:
        st.info("이 카테고리에는 상품이 아직 없습니다.")
        return

    # 3열 그리드 생성
    cols = st.columns(3)
    
    for idx, p in enumerate(product_list):
        with cols[idx % 3]:
            with st.container(border=True):
                # 카테고리 뱃지 표시 (전체보기 탭일 때 유용)
                cat = p.get('category', 'Etc')
                st.caption(f"🏷️ {cat}")
                
                # 이미지 처리
                img = p['image_url'] if p.get('image_url') else "https://via.placeholder.com/150"
                st.image(img, use_container_width=True)
                
                # 상품명 및 설명
                st.subheader(p['name'])
                desc = p.get('description', '')
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                st.write(desc)
                
                st.markdown(f"**💰 가격: ${p['price']:,.0f}**")
                
                # 수량 입력 (Key에 tab_key를 섞어서 유니크하게 만듦)
                qty = st.number_input(
                    "수량", 
                    min_value=1, 
                    max_value=100, 
                    value=1, 
                    key=f"qty_{p['id']}_{tab_key}"
                )
                
                # 장바구니 버튼
                if st.button("장바구니 담기", key=f"add_{p['id']}_{tab_key}", use_container_width=True):
                    item = {
                        "product_id": p['id'],
                        "name": p['name'],
                        "price": p['price'],
                        "quantity": qty
                    }
                    st.session_state['cart'].append(item)
                    st.toast(f"✅ {p['name']} {qty}개가 담겼습니다!")

# ==========================================
# 4. 탭 별로 콘텐츠 렌더링
# ==========================================

# (1) 첫 번째 탭: 전체 상품 출력
with tabs[0]:
    show_product_grid(products, "ALL")

# (2) 나머지 탭: 각 카테고리에 맞는 상품만 필터링해서 출력
for i, category_name in enumerate(categories):
    # tabs[0]은 전체보기니까, tabs[i+1]부터 사용
    with tabs[i + 1]:
        # 파이썬 리스트 컴프리헨션으로 필터링
        filtered_products = [p for p in products if p.get('category', 'Etc') == category_name]
        show_product_grid(filtered_products, category_name)