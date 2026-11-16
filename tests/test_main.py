from unittest.mock import patch, MagicMock
import pytest
from main import mcp, web_search, web_fetch


@pytest.fixture
def mock_ddgs():
    with patch("main.DDGS") as mock:
        yield mock


@pytest.fixture
def mock_trafilatura():
    with patch("main.trafilatura") as mock:
        yield mock


def test_web_search_success(mock_ddgs):
    # Arrange
    mock_ddgs_instance = mock_ddgs.return_value.__enter__.return_value
    mock_ddgs_instance.text.return_value = [
        {"title": "Result 1", "href": "https://example.com/1", "body": "Snippet 1"},
        {"title": "Result 2", "href": "https://example.com/2", "body": "Snippet 2"},
    ]

    # Act
    results = web_search("test query", max_results=2)

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
    results = web_search("non-existent query")

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
