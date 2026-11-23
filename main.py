import sys
from fastmcp import FastMCP
from ddgs import DDGS
from ddgs.exceptions import DDGSException
import trafilatura
import httpx
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from loguru import logger
from server_settings import ServerSettings

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

settings = ServerSettings()

logger.info(f"Starting MCP server '{settings.SERVER_NAME}' on {settings.HOST}:{settings.PORT}")

mcp = FastMCP(settings.SERVER_NAME)

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
    logger.info(f"web_search_ddg called: query='{query}', max_results={max_results}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            logger.info(f"web_search_ddg success: {len(results)} results")
            return results
    except DDGSException as e:
        logger.error(f"web_search_ddg error: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def web_search_bing(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Bing and return titles, URLs, and snippets."""
    logger.info(f"web_search_bing called: query='{query}', max_results={max_results}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results, backend='bing'))
            logger.info(f"web_search_bing success: {len(results)} results")
            return results
    except DDGSException as e:
        logger.error(f"web_search_bing error: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def web_fetch(url: str) -> str:
    """Fetch a webpage and extract its main content as clean Markdown."""
    logger.info(f"web_fetch called: url='{url}'")
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning(f"web_fetch failed to download: url='{url}'")
            return "Failed to fetch URL."
        text = trafilatura.extract(downloaded, output_format="markdown", include_links=True)
        logger.info(f"web_fetch success: url='{url}'")
        return text or "No readable content extracted."
    except Exception as e:
        logger.error(f"web_fetch error: url='{url}', error={e}")
        return f"Error: {str(e)}"

@mcp.tool()
def web_fetch_pdf(url: str) -> bytes:
    """Fetch a PDF file from a URL and return its binary content unaltered."""
    logger.info(f"web_fetch_pdf called: url='{url}'")
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            logger.info(f"web_fetch_pdf success: url='{url}', size={len(response.content)} bytes")
            return response.content
    except httpx.HTTPStatusError as e:
        logger.error(f"web_fetch_pdf error: url='{url}', HTTP error {e.response.status_code}")
        return f"Failed to fetch PDF: HTTP error {e.response.status_code}".encode()
    except httpx.TimeoutException:
        logger.error(f"web_fetch_pdf error: url='{url}', request timed out")
        return b"Failed to fetch PDF: Request timed out"
    except httpx.RequestError as e:
        logger.error(f"web_fetch_pdf error: url='{url}', request error - {str(e)}")
        return f"Failed to fetch PDF: Request error - {str(e)}".encode()
    except Exception as e:
        logger.error(f"web_fetch_pdf error: url='{url}', unexpected error - {str(e)}")
        return f"Failed to fetch PDF: Unexpected error - {str(e)}".encode()

if __name__ == "__main__":
    logger.info(f"Exposing Streamable HTTP at http://{settings.HOST}:{settings.PORT}/mcp")
    mcp.run(transport="http", host=settings.HOST, port=settings.PORT, middleware=middleware)
