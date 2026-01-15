class OrderAPI:
    def __init__(self, client):
        self.client = client

    def create_bulk(self, items):
        # items: [{'product_id': 1, 'quantity': 2}, ...]
        data = {"orders": items}
        return self.client.request("POST", "/orders/bulk/", json=data)