from fastmcp import FastMCP
from ddgs import DDGS
import trafilatura
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

app = mcp.http_app(middleware=middleware)

@mcp.tool()
def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web and return titles, URLs, and snippets."""
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))

@mcp.tool()
def web_fetch(url: str) -> str:
    """Fetch a webpage and extract its main content as clean Markdown."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return "Failed to fetch URL."
    text = trafilatura.extract(downloaded, output_format="markdown", include_links=True)
    return text or "No readable content extracted."

if __name__ == "__main__":
    # Exposes Streamable HTTP at http://127.0.0.1:8000/mcp
    mcp.run(transport="http", host="0.0.0.0", port=8000)