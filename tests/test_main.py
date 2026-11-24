from unittest.mock import MagicMock, patch

import httpx
import pytest
from main import web_fetch, web_fetch_pdf, web_search_ddg


@pytest.fixture
def mock_ddgs():
    with patch("main.DDGS") as mock:
        yield mock


@pytest.fixture
def mock_trafilatura():
    with patch("main.trafilatura") as mock:
        yield mock


@pytest.fixture
def mock_httpx():
    with patch("main.httpx.AsyncClient") as mock:
        yield mock


def test_web_search_success(mock_ddgs):
    # Arrange
    mock_ddgs_instance = mock_ddgs.return_value.__enter__.return_value
    mock_ddgs_instance.text.return_value = [
        {"title": "Result 1", "href": "https://example.com/1", "body": "Snippet 1"},
        {"title": "Result 2", "href": "https://example.com/2", "body": "Snippet 2"},
    ]

    # Act
    results = web_search_ddg("test query", max_results=2)

    # Assert
    assert len(results) == 2
    assert results[0]["title"] == "Result 1"
    assert results[0]["href"] == "https://example.com/1"
    assert results[0]["body"] == "Snippet 1"
    mock_ddgs_instance.text.assert_called_once_with("test query", max_results=2)


def test_web_search_empty(mock_ddgs):
    # Arrange
    mock_ddgs_instance = mock_ddgs.return_value.__enter__.return_value
    mock_ddgs_instance.text.return_value = []

    # Act
    results = web_search_ddg("non-existent query")

    # Assert
    assert results == []
    mock_ddgs_instance.text.assert_called_once_with("non-existent query", max_results=5)


def test_web_fetch_success(mock_trafilatura):
    # Arrange
    mock_trafilatura.fetch_url.return_value = b"html content"
    mock_trafilatura.extract.return_value = "# Sample Page\n\nHello world"

    # Act
    content = web_fetch("https://example.com")

    # Assert
    assert content == "# Sample Page\n\nHello world"
    mock_trafilatura.fetch_url.assert_called_once_with("https://example.com")
    mock_trafilatura.extract.assert_called_once_with(
        b"html content", output_format="markdown", include_links=True
    )


def test_web_fetch_failed_download(mock_trafilatura):
    # Arrange
    mock_trafilatura.fetch_url.return_value = None

    # Act
    content = web_fetch("https://not-real.com")

    # Assert
    assert content == "Failed to fetch URL."


def test_web_fetch_no_content(mock_trafilatura):
    # Arrange
    mock_trafilatura.fetch_url.return_value = b"<html></html>"
    mock_trafilatura.extract.return_value = None

    # Act
    content = web_fetch("https://empty.com")

    # Assert
    assert content == "No readable content extracted."


async def test_web_fetch_pdf_success(mock_httpx):
    # Arrange
    mock_response = MagicMock()
    mock_response.content = b"%PDF-1.4 fake pdf content"
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()

    async def mock_get(*args, **kwargs):
        return mock_response

    mock_client.get = mock_get
    mock_httpx.return_value.__aenter__.return_value = mock_client
    mock_httpx.return_value.__aexit__.return_value = None

    # Act
    content = await web_fetch_pdf("https://example.com/document.pdf")

    # Assert
    assert content == b"%PDF-1.4 fake pdf content"
    mock_response.raise_for_status.assert_called_once()


async def test_web_fetch_pdf_http_error(mock_httpx):
    # Arrange
    mock_client = MagicMock()
    mock_client.get = MagicMock(side_effect=httpx.HTTPStatusError("HTTP error", request=None, response=MagicMock(status_code=404)))
    mock_httpx.return_value.__aenter__.return_value = mock_client
    mock_httpx.return_value.__aexit__.return_value = None

    # Act
    content = await web_fetch_pdf("https://example.com/document.pdf")

    # Assert
    assert b"Failed to fetch PDF" in content


async def test_web_fetch_pdf_timeout_error(mock_httpx):
    # Arrange
    mock_client = MagicMock()
    mock_client.get = MagicMock(side_effect=httpx.TimeoutException("Timeout"))
    mock_httpx.return_value.__aenter__.return_value = mock_client
    mock_httpx.return_value.__aexit__.return_value = None

    # Act
    content = await web_fetch_pdf("https://example.com/document.pdf")

    # Assert
    assert b"Failed to fetch PDF" in content


async def test_web_fetch_pdf_request_error(mock_httpx):
    # Arrange
    mock_client = MagicMock()
    mock_client.get = MagicMock(side_effect=httpx.RequestError("Connection error"))
    mock_httpx.return_value.__aenter__.return_value = mock_client
    mock_httpx.return_value.__aexit__.return_value = None

    # Act
    content = await web_fetch_pdf("https://example.com/document.pdf")

    # Assert
    assert b"Failed to fetch PDF" in content
