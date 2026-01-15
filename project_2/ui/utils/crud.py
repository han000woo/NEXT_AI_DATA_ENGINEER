import os
import requests

# Docker Compose 환경변수 API_URL
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def get_products():
    try:
        res = requests.get(f"{API_BASE_URL}/products/")
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def create_product(data):
    try:
        res = requests.post(f"{API_BASE_URL}/products/", json=data)
        return res.status_code == 200
    except :
        return False

def create_order(product_id, quantity):
    try:
        data = {"product_id": product_id, "quantity": quantity}
        res = requests.post(f"{API_BASE_URL}/orders/", json=data)
        return res.status_code == 200
    except:
        return False