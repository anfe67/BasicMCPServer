import asyncio
import pytest
from main import mcp

@pytest.mark.asyncio
async def test_mcp_tools_registered():
    # Check if web_search is registered
    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}
    
    assert "web_search_ddg" in tool_names
    assert "web_search_bing" in tool_names
    assert "web_fetch" in tool_names
    assert "web_fetch_pdf" in tool_names

    # Check tool descriptions
    web_search_ddg_tool = next(tool for tool in tools if tool.name == "web_search_ddg")
    assert web_search_ddg_tool.description == "Search the web using DuckDuckGo and return titles, URLs, and snippets."

    web_search_bing_tool = next(tool for tool in tools if tool.name == "web_search_bing")
    assert web_search_bing_tool.description == "Search the web using Bing and return titles, URLs, and snippets."

    web_fetch_tool = next(tool for tool in tools if tool.name == "web_fetch")
    assert web_fetch_tool.description == "Fetch a webpage and extract its main content as clean Markdown."

    web_fetch_pdf_tool = next(tool for tool in tools if tool.name == "web_fetch_pdf")
    assert web_fetch_pdf_tool.description == "Fetch a PDF file from a URL and return its binary content unaltered."
