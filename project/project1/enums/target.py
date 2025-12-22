from enum import Enum

class AnswerTarget(Enum):
    PASTOR_A = "목사님A"
    PASTOR_B = "목사님B"
    PHILOSOPHER_A = "철학자A"

class SermonState(Enum):
    FOUND = "설교 기반 답변"      # 설교집에서 적절한 내용을 찾았을 때
    NOT_FOUND = "일반 위로 답변"   # 설교집에 내용이 없어 AI 지식으로 답변할 때
    BIBLE_ONLY = "성경 기반 답변"  # (추후 확장용) 성경 구절만 참고했을 때
    ERROR = "데이터 오류"          # DB 연결 등에 문제가 있을 때

TARGET_CONFIG = {
    AnswerTarget.PASTOR_A: {
        "system_prompt": "당신은 온화하고 지혜로운 목사님 A입니다. 공감과 설교체로 답하십시오.",
        "use_rag": True,
    },
    AnswerTarget.PASTOR_B: {
        "system_prompt": "당신은 직설적이지만 따뜻한 목사님 B입니다. 현실적인 권면을 해주십시오.",
        "use_rag": True,
    },
    AnswerTarget.PHILOSOPHER_A: {
        "system_prompt": "당신은 고대 철학자입니다. 논리적이고 사색적인 어조로 답하십시오.",
        "use_rag": False,
    },
}