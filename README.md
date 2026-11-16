# Knowsearch: Minimal MCP Server

A minimal MCP (Model Context Protocol) server that provides web search and web fetching capabilities.

## Features

- **Web Search**: Search the web using DuckDuckGo and retrieve titles, URLs, and snippets.
- **Web Fetch**: Fetch a webpage and extract its main content as clean Markdown using Trafilatura.

## Installation

Ensure you have Python 3.12+ and `uv` installed.

```bash
uv sync
```

## Running the server

```bash
uv run python main.py
```

The server will be available via HTTP at `http://127.0.0.1:8000/mcp`.

## Running tests

```bash
uv run pytest
```

## Project structure

- `main.py`: Entry point containing the FastMCP server definition and tools.
- `pyproject.toml`: Project configuration and dependencies.
- `tests/`: Test suite.
- `embedder/`: Optional directory for embedding functionality.
- `Dockerfile` & `docker-compose.yml`: Containerization configuration.

## Deployment

To run this server in a production environment, build the Docker image and expose port 8000 so that `llama-server` can call the MCP endpoint at `http://<host>:8000/mcp`.

**Build the image**:
```
docker build -t basic-mcp-server .
```

**Run the container**:
```
docker run -d --name basic-mcp-server -p 8000:8000 basic-mcp-server
```

Alternatively, use `docker-compose`:
```
docker-compose up -d
```

The container will listen on `0.0.0.0:8000` and expose the MCP endpoint at `/mcp`. Verify with:
```
curl http://localhost:8000/mcp
```

Adjust the host in `main.py` if you need a different binding address.
