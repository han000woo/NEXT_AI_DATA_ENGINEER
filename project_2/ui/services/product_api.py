class ProductAPI:
    def __init__(self, client):
        self.client = client  # Core Client 주입

    def get_list(self):
        return self.client.request("GET", "/products/") or []

    def create(self, data):
        return self.client.request("POST", "/products/", json=data)

    def update(self, product_id, data):
        return self.client.request("PUT", f"/products/{product_id}", json=data)

    def delete(self, product_id):
        return self.client.request("DELETE", f"/products/{product_id}")