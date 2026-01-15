from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
import os


MCP_SERVER_URL = os.getenv("MCP_NEWS_URL", "http://localhost:8000/sse")
print(f"🔗 접속 시도 중인 MCP 서버 주소: {MCP_SERVER_URL}") # 로그로 확인 가능
# ---------------------------------------------------------
# 서버에서 뉴스 가져오기 (도구 사용)
# ---------------------------------------------------------
async def get_news_from_mcp(search_keyword):
    """MCP 서버에 접속해서 get_latest_news 도구를 실행함"""
    try:
        async with sse_client(MCP_SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                # 도구 실행 요청
                result = await session.call_tool(
                    "get_latest_news",
                    arguments={"keyword": search_keyword, "limit": 2}
                )
                # 결과 텍스트 반환
                return result.content[0].text
            
    except Exception as e:
        return f"Error: MCP 서버 연결 실패 ({str(e)})"

# ---------------------------------------------------------
# MySQL서버에 저장 
# ---------------------------------------------------------
async def mcp_save_log(user_input: str, mento_name: str): 
    """
    MCP 서버에 접속해서 전체 대화 내용을 전달하고, 
    서버가 분석 및 저장을 수행하도록 요청함
    """
    print(f"📡 MCP 서버로 데이터 전송 시작... (멘토: {mento_name})")
    
    try:
        # 1. 서버 연결 (SSE 방식)
        async with sse_client(MCP_SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                # 2. 도구 실행 요청 (서버의 analyze_and_save_log 함수 호출)
                # 주의: arguments의 키값은 서버 함수(analyze_and_save_log)의 인자 이름과 똑같아야 함!
                result = await session.call_tool(
                    "analyze_and_save_log",
                    arguments={
                        "user_input": user_input, 
                        "mento": mento_name
                    }
                )
                
                # 3. 결과 반환 (서버에서 보낸 "✅ 저장 완료" 메시지 받기)
                # result는 CallToolResult 객체이며, 실제 텍스트는 content 리스트 안에 있음
                output_text = result.content[0].text
                print(f"📬 서버 응답: {output_text}")
                return output_text

    except Exception as e:
        error_msg = f"Error: MCP 서버 연결 또는 도구 실행 실패 ({str(e)})"
        print(error_msg)
        return "❌ 데이터 저장에 실패했습니다."


# ---------------------------------------------------------
# 서버에서 DB에 조회
# ---------------------------------------------------------
async def mcp_query_db(tool_name, arguments):
    """실제 MCP 서버에 접속해서 도구를 실행하고 결과를 가져옴"""
    
    try:
        async with sse_client(MCP_SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                # 도구 호출
                result = await session.call_tool(
                    tool_name, 
                    arguments=arguments)
                
                # 결과 텍스트 추출 (리스트의 첫 번째 요소)
                return result.content[0].text
    except Exception as e:
        return f"통신 에러: {e}"