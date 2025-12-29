tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_period_analytics",
            "description": "특정 기간 동안의 상담 데이터(감정, 키워드, 멘토 빈도)를 통계 내어 분석함",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "조회 시작 날짜 (YYYY-MM-DD 형식). 사용자의 말에서 유추."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "조회 종료 날짜 (YYYY-MM-DD 형식). 오늘 날짜 기준 유추."
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["emotion_rank", "keyword_rank", "mento_rank"],
                        "description": "분석할 종류 (감정 순위, 키워드 순위, 멘토 빈도 중 택 1)"
                    }
                },
                "required": ["start_date", "end_date", "analysis_type"]
            }
        }
    },
    # 필요한 경우 search_past_logs 같은 다른 도구도 여기에 추가
]