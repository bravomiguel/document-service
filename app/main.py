"""FastAPI application for markdown to DOCX conversion service."""
import logging
import json
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request, status
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .models import ConvertRequest, HealthResponse, ErrorResponse
from .converter import convert_markdown_to_docx, get_pandoc_version, ConversionError
from .config import config

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(message)s'
)
logger = logging.getLogger(__name__)


# Custom JSON formatter for structured logs
class StructuredLogger:
    """Helper for structured JSON logging."""

    @staticmethod
    def log(level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        logger.log(getattr(logging, level), json.dumps(log_entry))


structured_logger = StructuredLogger()

# Create FastAPI application
app = FastAPI(
    title="Document Export Service",
    description="Converts markdown content to DOCX format",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()

    response = await call_next(request)

    duration_ms = int((time.time() - start_time) * 1000)

    # Only log non-health check requests at INFO level
    if request.url.path != "/health":
        structured_logger.log(
            "INFO",
            f"{request.method} {request.url.path}",
            request_id=request_id,
            duration_ms=duration_ms,
            status_code=response.status_code
        )

    return response


# Authentication helper
def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify API key from Authorization header.

    Args:
        authorization: Authorization header value (Bearer <token>)

    Returns:
        True if valid, raises HTTPException otherwise
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    # Extract Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )

    token = parts[1]

    # Constant-time comparison to prevent timing attacks
    if not _constant_time_compare(token, config.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return True


def _constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    structured_logger.log(
        "WARNING",
        "Validation error",
        request_id=getattr(request.state, "request_id", "unknown"),
        errors=exc.errors()
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request", "details": str(exc)}
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.

    Returns service status and Pandoc version.
    """
    try:
        pandoc_version = get_pandoc_version()
        return HealthResponse(
            status="healthy",
            pandoc_version=pandoc_version,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


# Conversion endpoint
@app.post(
    "/api/v1/convert/docx",
    responses={
        200: {"description": "DOCX file", "content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}}},
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Conversion error"}
    },
    tags=["Conversion"]
)
async def convert_to_docx(
    request: Request,
    convert_request: ConvertRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Convert markdown content to DOCX format.

    Requires valid API key in Authorization header (Bearer token).

    Args:
        convert_request: Conversion request with markdown content and filename
        authorization: Authorization header with Bearer token

    Returns:
        DOCX file as binary stream
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Verify API key
    verify_api_key(authorization)

    # Log conversion start
    content_size = len(convert_request.content.encode('utf-8'))
    structured_logger.log(
        "INFO",
        "Starting conversion",
        request_id=request_id,
        content_size_bytes=content_size,
        filename=convert_request.filename
    )

    try:
        # Perform conversion
        start_time = time.time()
        docx_bytes = convert_markdown_to_docx(
            convert_request.content,
            convert_request.filename
        )
        duration_ms = int((time.time() - start_time) * 1000)

        # Log success
        structured_logger.log(
            "INFO",
            "Conversion successful",
            request_id=request_id,
            duration_ms=duration_ms,
            content_size_bytes=content_size,
            output_size_bytes=len(docx_bytes)
        )

        # Return DOCX file
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{convert_request.filename}"'
            }
        )

    except ValueError as e:
        # Invalid input (empty content, too large, etc.)
        structured_logger.log(
            "WARNING",
            "Invalid input",
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except ConversionError as e:
        # Conversion failed
        structured_logger.log(
            "ERROR",
            "Conversion failed",
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        )

    except Exception as e:
        # Unexpected error
        structured_logger.log(
            "ERROR",
            "Unexpected error",
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log service startup."""
    structured_logger.log(
        "INFO",
        "Document export service started",
        pandoc_version=get_pandoc_version(),
        config={
            "max_content_size_mb": config.MAX_CONTENT_SIZE_MB,
            "allowed_origins": config.ALLOWED_ORIGINS
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
