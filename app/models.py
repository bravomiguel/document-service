"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional


class ConvertRequest(BaseModel):
    """Request model for markdown to DOCX conversion."""

    content: str = Field(..., description="Markdown content to convert")
    filename: Optional[str] = Field(
        default="export.docx",
        description="Output filename",
        pattern=r"^[\w\s\-\.]+\.docx$"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "# Hello World\n\nThis is a **test** document.",
                "filename": "test.docx"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    pandoc_version: str = Field(..., description="Pandoc version")
    timestamp: str = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
