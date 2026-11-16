from fastmcp import FastMCP
from ddgs import DDGS
import trafilatura
from fastapi.middleware.cors import CORSMiddleware

mcp = FastMCP("Local Web Search")

# Add CORS middleware to allow cross-origin requests
app = mcp.http_app()
app.add_middleware(  # type: ignore
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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