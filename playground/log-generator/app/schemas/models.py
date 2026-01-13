from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union

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

# LLM이 결정할 각 컬럼의 정보
class ColumnDefinition(BaseModel):
    name: str = Field(..., description="컬럼(필드) 이름 (예: user_id, price)")
    data_type: Literal['name', 'email', 'date', 'uuid', 'int', 'float', 'city', 'country', 'category'] = Field(..., description="데이터 타입")
    options: List[str] = Field(default=[], description="category 타입일 경우 선택지 (예: ['Buy', 'Sell'])")

# LLM이 최종적으로 반환할 도구 호출 인자 구조
class DynamicLogRequest(BaseModel):
    table_name: str = Field(..., description="로그의 주제 (예: stock_trades)")
    count: int = Field(default=5, description="생성할 로그 개수")
    columns: List[ColumnDefinition] = Field(..., description="생성할 컬럼 목록")


# 컬럼의 세부 설정 (사용자가 UI에서 입력할 내용)
class CustomColumnDefinition(BaseModel):
    name: str
    type: Literal['int', 'float', 'string', 'date', 'category', 'uuid']
    min_value: Optional[Union[float, str]] = None 
    max_value: Optional[Union[float, str]] = None
    options: Optional[List[str]] = None

# 스키마 저장용 모델
class SchemaConfig(BaseModel):
    schema_name: str
    description: Optional[str] = ""
    columns: List[CustomColumnDefinition]

# 데이터 생성 요청 모델
class GenerateCustomRequest(BaseModel):
    count: int = 10
    config: SchemaConfig