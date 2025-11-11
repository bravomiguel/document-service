"""Markdown to DOCX conversion logic using Pandoc."""
import os
import tempfile
import pypandoc
from typing import Optional
from .config import config
import logging

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raised when conversion fails."""
    pass


def convert_markdown_to_docx(
    markdown_content: str,
    output_filename: str = "export.docx"
) -> bytes:
    """
    Convert markdown content to DOCX format using Pandoc.

    Args:
        markdown_content: Markdown string to convert
        output_filename: Desired output filename (for metadata)

    Returns:
        DOCX file content as bytes

    Raises:
        ConversionError: If conversion fails
        ValueError: If content is empty or invalid
    """
    # Validate input
    if not markdown_content or not markdown_content.strip():
        raise ValueError("Empty content provided")

    # Check content size
    content_size = len(markdown_content.encode('utf-8'))
    if content_size > config.MAX_CONTENT_SIZE_BYTES:
        raise ValueError(
            f"Content too large: {content_size} bytes "
            f"(max: {config.MAX_CONTENT_SIZE_BYTES} bytes)"
        )

    # Sanitize content (remove script tags if present)
    sanitized_content = markdown_content.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")

    # Create temporary file for output
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        logger.info(f"Starting conversion, content size: {content_size} bytes")

        # Pandoc conversion options
        extra_args = [
            '--quiet',  # Reduce overhead
        ]

        # Add reference document if available
        if os.path.exists(config.REFERENCE_DOCX_PATH):
            extra_args.extend(['--reference-doc', config.REFERENCE_DOCX_PATH])
            logger.debug(f"Using reference document: {config.REFERENCE_DOCX_PATH}")

        # Convert markdown to DOCX
        pypandoc.convert_text(
            sanitized_content,
            'docx',
            format='markdown',
            outputfile=tmp_path,
            extra_args=extra_args
        )

        # Read the generated file
        with open(tmp_path, 'rb') as f:
            docx_bytes = f.read()

        logger.info(f"Conversion successful, output size: {len(docx_bytes)} bytes")
        return docx_bytes

    except pypandoc.PandocException as e:
        logger.error(f"Pandoc conversion failed: {str(e)}")
        raise ConversionError(f"Pandoc conversion failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")
        raise ConversionError(f"Conversion error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {tmp_path}: {e}")


def get_pandoc_version() -> str:
    """
    Get the installed Pandoc version.

    Returns:
        Pandoc version string

    Raises:
        ConversionError: If Pandoc is not available
    """
    try:
        version = pypandoc.get_pandoc_version()
        return version
    except Exception as e:
        logger.error(f"Failed to get Pandoc version: {e}")
        raise ConversionError(f"Pandoc not available: {str(e)}")
