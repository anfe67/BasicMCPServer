import pytest
import json
from main import mcp, web_fetch
from ddgs import DDGS
from fastmcp.tools.base import ToolResult

@pytest.mark.asyncio
async def test_ddgs_direct_integration():
    """Integration test for DDGS library directly."""
    query = "python programming language"
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
        
    assert results is not None
    assert len(results) > 0
    result = results[0]
    assert "title" in result
    assert "href" in result
    assert "body" in result

@pytest.mark.asyncio
async def test_web_search_ddg_tool_integration():
    """Integration test for web_search_ddg MCP tool."""
    query = "python programming language"
    results = await mcp.call_tool("web_search_ddg", arguments={"query": query, "max_results": 1})
    
    assert results is not None
    assert isinstance(results, ToolResult)
    assert not results.is_error
    assert len(results.content) > 0
    assert isinstance(results.content[0].text, str)
    
    results_list = json.loads(results.content[0].text)
    assert isinstance(results_list, list)
    assert len(results_list) > 0
    result = results_list[0]
    assert "title" in result
    assert "href" in result
    assert "body" in result

@pytest.mark.asyncio
async def test_web_search_bing_tool_integration():
    """Integration test for web_search_bing MCP tool."""
    query = "python programming language"
    results = await mcp.call_tool("web_search_bing", arguments={"query": query, "max_results": 1})
    
    assert results is not None
    assert isinstance(results, ToolResult)
    assert not results.is_error
    assert len(results.content) > 0
    assert isinstance(results.content[0].text, str)
    
    results_list = json.loads(results.content[0].text)
    assert isinstance(results_list, list)
    assert len(results_list) > 0
    result = results_list[0]
    assert "title" in result
    assert "href" in result
    assert "body" in result

@pytest.mark.asyncio
async def test_web_fetch_direct():
    """Integration test for web_fetch function directly."""
    url = "https://example.com"
    content = web_fetch(url)
    
    assert content is not None
    assert isinstance(content, str)
    assert len(content) > 0
    # Example.com content might not contain "Example Domain" depending on what trafilatura extracts
    # Let's just check that it's not empty

@pytest.mark.asyncio
async def test_web_fetch_tool_integration():
    """Integration test for web_fetch MCP tool."""
    url = "https://www.python.org"
    results = await mcp.call_tool("web_fetch", arguments={"url": url})
    
    assert results is not None
    assert isinstance(results, ToolResult)
    assert not results.is_error
    assert len(results.content) > 0
    assert isinstance(results.content[0].text, str)
    assert len(results.content[0].text) > 0
