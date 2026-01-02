from datetime import datetime, time
import json
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import feedparser
import urllib.parse
import mysql.connector
from openai import OpenAI
from collections import Counter

# 'News-Agent'라는 이름의 서버 생성
mcp = FastMCP("News-Agent", host="0.0.0.0", port=8000)

# 1. .env 파일의 내용을 환경변수로 로드합니다.
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY가 없습니다!")
else:
    print(f"✅ API Key 로드 성공 (길이: {len(api_key)})")

client = OpenAI(api_key=api_key)

# 2. os.getenv를 사용해 값을 가져옵니다.
DB_CONFIG = {
    "host": os.getenv(
        "DB_HOST", "localhost"
    ),  # 값이 없으면 localhost를 기본값으로 사용
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),  # .env에 반드시 있어야 함
    "database": os.getenv("DB_NAME", "counseling_db"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "use_unicode": True,
}


def get_connection():
    """MySQL 데이터베이스 연결을 생성하는 헬퍼 함수"""
    retries = 10
    while retries > 0:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except SystemError as e:
            print(f"⏳ DB 연결 대기 중... (남은 시도: {retries}) - {e}")
            retries -= 1
            time.sleep(5)  # 5초 대기

    raise Exception("❌ DB 연결 실패: 데이터베이스가 응답하지 않습니다.")


def init_db():
    """테이블이 없으면 생성 (최초 1회 실행용)"""
    try:
        # DB 연결 (DB가 없으면 생성하는 로직은 복잡하므로, 미리 DB는 만들어두는 것을 권장)
        conn = get_connection()
        cursor = conn.cursor()

        # 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS counseling_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATETIME,
            mento VARCHAR(50),
            user_input TEXT,
            keywords VARCHAR(255),
            emotion VARCHAR(50)
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ MySQL 테이블 확인/생성 완료")
    except mysql.connector.Error as err:
        print(f"❌ DB 초기화 에러: {err}")
    finally:
        if "conn" in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ---------------------------------------------------------
# [2] 상담 로그 저장 도구 (MySQL 버전)
# ---------------------------------------------------------
@mcp.tool()
def analyze_and_save_log(user_input: str, mento: str) -> str:
    """
    [서버 측 로직]
    대화 전체 기록(full_dialogue)을 받아서,
    서버가 직접 키워드와 감정을 추출(LLM)한 뒤 DB에 저장합니다.

    Args:
        full_dialogue: "User: 안녕\nMento: 반가워요..." 형태의 전체 대화 문자열
        mento_name: 멘토 이름
    """
    try:
        # 1. MCP 서버가 직접 LLM에게 분석 요청 (GPT-4o-mini 사용 추천)
        prompt = f"""
        아래 사용자 질문을 분석해서 JSON으로 반환해줘.
        
        [사용자 질문]
        {user_input}
        
        [요구사항]
        1. keywords: 핵심 주제 3개 (쉼표 구분)
        2. emotion: 내담자의 감정 1단어
        3. summary: 1줄 요약
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 전문 상담 분석가야."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        # JSON 파싱
        content = response.choices[0].message.content
        cleaned_json = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_json)

        keywords = data.get("keywords", "미정")
        emotion = data.get("emotion", "보통")
        summary = data.get("summary", "")

        # 2. DB 저장
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO counseling_logs (date, mento, user_input, keywords, emotion)
            VALUES (%s, %s, %s, %s, %s)
        """
        # user_input 컬럼에는 '요약본(summary)'을 저장하는 게 더 효율적일 수 있습니다.
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(sql, (now, mento, summary, keywords, emotion))
        conn.commit()

        return f"✅ 서버 분석 및 저장 완료! (감정: {emotion}, 키워드: {keywords})"

    except Exception as e:
        return f"❌ 서버 오류: {str(e)}"
    finally:
        if "conn" in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@mcp.tool()
def get_latest_news(keyword: str = "사회", limit: int = 3) -> str:
    """구글 뉴스에서 키워드 검색 결과를 가져옵니다."""
    encoded_keyword = urllib.parse.quote(keyword)
    rss_url = (
        f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    )

    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return "뉴스를 찾을 수 없습니다."

    results = []
    for i, entry in enumerate(feed.entries[:limit]):
        results.append(f"[{i+1}] {entry.title} ({entry.published})")

    return "\n".join(results)


import json
from collections import Counter


@mcp.tool()
def get_period_analytics(start_date: str, end_date: str, analysis_type: str) -> str:
    """
    특정 기간 동안의 상담 데이터를 분석하여 JSON 형식으로 반환합니다.
    시각화(차트, 워드클라우드)를 위해 사용됩니다.

    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        analysis_type: 'emotion_rank', 'keyword_rank', 'mento_rank' 중 하나

    Returns:
        JSON String (예: '[{"label": "불안", "value": 10}, ...]')
    """
    conn = get_connection()
    cursor = conn.cursor()

    date_condition = "date >= %s AND date <= %s"
    full_end_date = f"{end_date} 23:59:59"

    result_data = []  # 데이터를 담을 리스트

    try:
        # 1. 감정 상태 순위
        if analysis_type == "emotion_rank":
            sql = f"""
                SELECT emotion, COUNT(*) as cnt 
                FROM counseling_logs 
                WHERE {date_condition}
                GROUP BY emotion 
                ORDER BY cnt DESC
            """
            cursor.execute(sql, (start_date, full_end_date))
            rows = cursor.fetchall()

            # JSON 구조: [{"emotion": "불안", "count": 10}, ...]
            for row in rows:
                result_data.append({"emotion": row[0], "count": row[1]})

        # 2. 멘토 호출 횟수 순위
        elif analysis_type == "mento_rank":
            sql = f"""
                SELECT mento, COUNT(*) as cnt 
                FROM counseling_logs 
                WHERE {date_condition}
                GROUP BY mento 
                ORDER BY cnt DESC
            """
            cursor.execute(sql, (start_date, full_end_date))
            rows = cursor.fetchall()

            # JSON 구조: [{"mento": "니체", "count": 5}, ...]
            for row in rows:
                result_data.append({"mento": row[0], "count": row[1]})

        # 3. 고민 키워드 순위
        elif analysis_type == "keyword_rank":
            sql = f"SELECT keywords FROM counseling_logs WHERE {date_condition}"
            cursor.execute(sql, (start_date, full_end_date))
            rows = cursor.fetchall()

            all_words = []
            for row in rows:
                if row[0]:
                    words = [w.strip() for w in row[0].split(",")]
                    all_words.extend(words)

            # 워드클라우드용 데이터는 좀 더 많이 가져옵니다 (Top 10)
            top_keywords = Counter(all_words).most_common(10)

            # JSON 구조: [{"keyword": "취업", "count": 15}, ...]
            for word, cnt in top_keywords:
                result_data.append({"keyword": word, "count": cnt})

        else:
            return json.dumps({"error": "잘못된 분석 타입입니다."}, ensure_ascii=False)

        # Python 객체(List/Dict)를 JSON 문자열로 변환 (한글 깨짐 방지)
        return json.dumps(result_data, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"분석 중 오류 발생: {str(e)}"}, ensure_ascii=False)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Docker 통신을 위해 0.0.0.0 주소의 8000 포트로 엽니다.
    # mcp.run(transport="sse", host="0.0.0.0", port=8000)
    try:
        init_db()
        print("✅ DB 초기화 완료", flush=True)  # flush=True는 즉시 출력을 의미
    except Exception as e:
        print(f"⚠️ DB 에러: {e}", flush=True)
    mcp.run(transport="sse")
