import os
import requests
import streamlit as st

class APIClient:
    """
    기본적인 HTTP 요청을 처리하는 Core Client입니다.
    """
    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://127.0.0.1:8000")
        self.session = requests.Session()
        print(f"📡 API Client connected to {self.base_url}")

    def request(self, method, endpoint, **kwargs):
        """
        모든 요청은 이 함수를 통과합니다. (공통 에러 처리 용이)
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            
            # 200~299 사이면 성공으로 간주
            if 200 <= response.status_code < 300:
                # 내용이 있으면 JSON, 없으면 True 반환
                return response.json() if response.content else True
            else:
                print(f"⚠️ API Error [{response.status_code}]: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None