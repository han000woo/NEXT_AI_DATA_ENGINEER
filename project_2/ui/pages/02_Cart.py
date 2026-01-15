import streamlit as st
import pandas as pd
import time
from services import get_api

api = get_api()

st.set_page_config(page_title="Shopping Cart", layout="wide")

# CSS: 테이블 헤더 스타일 및 여백 조정
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .header-text {
        font-weight: bold;
        color: #555;
    }
    .total-area {
        font-size: 1.2rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Shopping Cart")
st.markdown("---")

# 장바구니 비었을 때 처리
if 'cart' not in st.session_state or len(st.session_state['cart']) == 0:
    st.container(border=True).markdown(
        """
        <div style='text-align: center; padding: 50px;'>
            <h3>장바구니가 비어있습니다.</h3>
            <p style='color: gray;'>원하는 상품을 담아주세요.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.stop()

# 1. 장바구니 리스트 헤더 (Custom Grid)
# 비율: 상품명(3) | 수량(1) | 단가(1) | 합계(1)
h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
h1.markdown("<span class='header-text'>PRODUCT</span>", unsafe_allow_html=True)
h2.markdown("<span class='header-text'>QUANTITY</span>", unsafe_allow_html=True)
h3.markdown("<span class='header-text'>PRICE</span>", unsafe_allow_html=True)
h4.markdown("<span class='header-text'>TOTAL</span>", unsafe_allow_html=True)

st.divider()

# 2. 개별 상품 렌더링
total_amount = 0

for item in st.session_state['cart']:
    # 데이터 계산
    line_total = item['quantity'] * item['price']
    total_amount += line_total
    
    # 행 출력
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    
    with c1:
        st.write(f"**{item['name']}**")
        # st.caption(item.get('description', '')) # 설명이 있다면 추가 가능
    
    with c2:
        st.write(f"{item['quantity']} EA")
        
    with c3:
        st.write(f"{item['price']:,.0f} USD")
        
    with c4:
        st.write(f"**{line_total:,.0f} USD**")
    
    # 행 간 간격 조정을 위한 빈 공간 (선택사항)
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

st.divider()

# 3. 결제 요약 및 액션 (Card UI)
# 화면 오른쪽으로 정렬된 느낌을 주기 위해 빈 컬럼 사용
spacer, summary_col = st.columns([2, 2])

with summary_col:
    with st.container(border=True):
        st.subheader("Order Summary")
        
        # 총액 표시 (Metric 컴포넌트 활용)
        st.metric(
            label="Total Payment", 
            value=f"${total_amount:,.2f}"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 액션 버튼
        col_cancel, col_pay = st.columns([1, 2])
        
        with col_cancel:
            if st.button("Clear All"):
                st.session_state['cart'] = []
                st.rerun()
        
        with col_pay:
            # Primary 버튼으로 강조
            if st.button("Checkout", type="primary"):
                # 데이터 변환
                order_items = [
                    {'product_id': item['product_id'], 'quantity': item['quantity']}
                    for item in st.session_state['cart']
                ]

                # 서버 통신
                if api.order.create_bulk(order_items):
                    st.success("주문이 정상적으로 처리되었습니다.")
                    st.session_state['cart'] = [] # 초기화
                    time.sleep(1.5) # 메시지 확인 시간 부여
                    st.rerun()
                else:
                    st.error("서버 통신 오류가 발생했습니다.")