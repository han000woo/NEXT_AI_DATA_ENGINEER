from mcp.server.fastmcp import FastMCP
import feedparser
import urllib.parse

# 'News-Agent'라는 이름의 서버 생성
mcp = FastMCP("News-Agent")

@mcp.tool()
def get_latest_news(keyword: str = "사회", limit: int = 3) -> str:
    """구글 뉴스에서 키워드 검색 결과를 가져옵니다."""
    encoded_keyword = urllib.parse.quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return "뉴스를 찾을 수 없습니다."

    results = []
    for i, entry in enumerate(feed.entries[:limit]):
        results.append(f"[{i+1}] {entry.title} ({entry.published})")
    
    return "\n".join(results)

if __name__ == "__main__":
    # Docker 통신을 위해 0.0.0.0 주소의 8000 포트로 엽니다.
    # mcp.run(transport="sse", host="0.0.0.0", port=8000)
    mcp.run(transport="sse")
