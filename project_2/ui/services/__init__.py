import streamlit as st
from .client import APIClient
from .product_api import ProductAPI
from .order_api import OrderAPI

class AppAPI:
    """
    모든 도메인 API를 하나로 묶는 Wrapper 클래스
    사용 예: api.product.get_list()
    """
    def __init__(self):
        self.client = APIClient()  # Core Client 생성
        
        # 각 도메인 연결
        self.product = ProductAPI(self.client)
        self.order = OrderAPI(self.client)

# ============================================
# Singleton Instance Generator
# ============================================
@st.cache_resource
def get_api():
    return AppAPI()