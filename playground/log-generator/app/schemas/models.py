from pydantic import BaseModel
from typing import Literal


# 로그 데이터 구조 정의
class LogSchema(BaseModel):
    event_id: str
    timestamp: str
    user_id: int
    user_region: str
    event_type: Literal["click", "view", "purchase", "cart_add"]
    item_id: str
    price: float


# 요청 바디 정의
class GenerateRequest(BaseModel):
    count: int = 10
