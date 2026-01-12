import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from app.schemas.dynamic_models import DynamicLogRequest

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LLMHandler:
    @staticmethod
    def parse_prompt_to_schema(user_prompt: str) -> DynamicLogRequest:
        """
        사용자의 자연어 요청을 받아서 데이터 생성 스키마(JSON)로 변환합니다.
        """
        
        # 1. 사용할 도구(Tool) 정의
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "define_data_schema",
                    "description": "사용자 요청에 따라 더미 데이터 생성을 위한 스키마를 정의합니다.",
                    "parameters": DynamicLogRequest.model_json_schema()
                }
            }
        ]

        # 2. LLM 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 또는 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "당신은 데이터 엔지니어링 보조 도구입니다. 사용자의 요청을 분석하여 적절한 데이터 스키마를 생성하세요."},
                {"role": "user", "content": user_prompt}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "define_data_schema"}}
        )

        # 3. 결과 파싱 (수정된 부분)
        try:
            # 첫 번째 도구 호출(Tool Call) 객체 가져오기
            tool_call = response.choices[0].message.tool_calls[0]
            
            # [중요] 구조: tool_call -> function -> arguments (문자열)
            # tool_call.function_arguments (X) -> 없는 속성입니다.
            # tool_call.function.arguments (O) -> 올바른 접근입니다.
            arguments_str = tool_call.function.arguments
            
            # JSON 문자열을 딕셔너리로 변환
            arguments = json.loads(arguments_str)
            
            print(f"DEBUG: Parsed Arguments: {arguments}") # 디버깅용 출력
            
            # Pydantic 모델로 변환하여 반환
            return DynamicLogRequest(**arguments)
            
        except AttributeError as e:
            # LLM이 도구 호출을 제대로 반환하지 않았을 때의 예외 처리
            print(f"Structure Error: {e}")
            raise ValueError("LLM이 올바른 도구 호출 형식을 반환하지 않았습니다.")
        except json.JSONDecodeError:
            raise ValueError("LLM이 반환한 인자가 올바른 JSON 형식이 아닙니다.")