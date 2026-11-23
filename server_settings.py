from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Server configuration from environment variables."""

    model_config = SettingsConfigDict(env_prefix="BASIC_MCP_SERVER_")

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SERVER_NAME: str = "Local Web Search"
