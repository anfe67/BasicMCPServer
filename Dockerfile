FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy dependency files first to leverage cache
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtualenv
RUN uv sync --frozen

# Copy source code
COPY main.py .

# The app exposes HTTP at port 8000
EXPOSE 8000

# Use the uv-created virtualenv to run the application
CMD ["uv", "run", "python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
