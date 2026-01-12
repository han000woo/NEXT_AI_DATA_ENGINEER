from pydantic import BaseModel, Field
from typing import List, Literal

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