"""Configuration management for document service."""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # API Key for authentication
    API_KEY: str = os.getenv("EXPORT_SERVICE_API_KEY", "dev-secret-key-12345")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # Content limits
    MAX_CONTENT_SIZE_MB: int = int(os.getenv("MAX_CONTENT_SIZE_MB", "5"))
    MAX_CONTENT_SIZE_BYTES: int = MAX_CONTENT_SIZE_MB * 1024 * 1024

    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003"
    ).split(",")

    # Paths
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    REFERENCE_DOCX_PATH: str = os.path.join(TEMPLATES_DIR, "reference.docx")

    # Timeouts
    CONVERSION_TIMEOUT_SECONDS: int = 30


config = Config()
