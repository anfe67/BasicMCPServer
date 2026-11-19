from fastmcp import FastMCP
from ddgs import DDGS
from ddgs.exceptions import DDGSException
import trafilatura
import httpx
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

mcp = FastMCP("Local Web Search")

# Configure CORS middleware for browser-based clients
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (adjust for production)
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "mcp-protocol-version",
            "mcp-session-id",
            "mcp-method",
            "mcp-name",
            "Authorization",
            "Content-Type",
        ],
        expose_headers=["mcp-session-id"],
    )
]

@mcp.tool()
def web_search_ddg(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo and return titles, URLs, and snippets."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except DDGSException as e:
        return [{"error": str(e)}]

@mcp.tool()
def web_search_bing(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Bing and return titles, URLs, and snippets."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results, backend='bing'))
    except DDGSException as e:
        return [{"error": str(e)}]

@mcp.tool()
def web_fetch(url: str) -> str:
    """Fetch a webpage and extract its main content as clean Markdown."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return "Failed to fetch URL."
    text = trafilatura.extract(downloaded, output_format="markdown", include_links=True)
    return text or "No readable content extracted."

@mcp.tool()
def web_fetch_pdf(url: str) -> bytes:
    """Fetch a PDF file from a URL and return its binary content unaltered."""
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            return response.content
    except httpx.HTTPStatusError as e:
        return f"Failed to fetch PDF: HTTP error {e.response.status_code}".encode()
    except httpx.TimeoutException:
        return b"Failed to fetch PDF: Request timed out"
    except httpx.RequestError as e:
        return f"Failed to fetch PDF: Request error - {str(e)}".encode()
    except Exception as e:
        return f"Failed to fetch PDF: Unexpected error - {str(e)}".encode()

if __name__ == "__main__":
    # Exposes Streamable HTTP at http://0.0.0.0:8000/mcp
    mcp.run(transport="http", host="0.0.0.0", port=8000, middleware=middleware)
