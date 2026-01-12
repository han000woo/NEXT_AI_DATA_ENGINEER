from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from app.schemas.models import GenerateRequest, LogSchema
from app.services.generator import LogGeneratorService
from typing import List

from app.services.llm_handler import LLMHandler

app = FastAPI(title="Log Generator API")

# 요청 바디 정의
class PromptRequest(BaseModel) : 
    prompt : str 

@app.post("/generate-by-prompt")
def generate_by_prompt(req: PromptRequest):
    try:
        # 1. LLM을 통해 스키마 생성 (Tool Calling)
        schema = LLMHandler.parse_prompt_to_schema(req.prompt)
        
        # 2. 생성된 스키마로 실제 데이터 생성
        result = LogGeneratorService.generate_dynamic_logs(schema)
        
        return result
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
 