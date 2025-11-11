# Document Export Service

FastAPI-based microservice that converts TipTap editor markdown content to DOCX format using Pandoc.

## Features

- Markdown to DOCX conversion
- API key authentication
- Docker containerization
- Structured JSON logging
- Health check endpoint
- CORS support for Next.js dev servers
- Custom DOCX styling via reference template

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Running with Docker (Recommended)

1. **Navigate to the document-service directory:**
   ```bash
   cd document-service
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and set EXPORT_SERVICE_API_KEY if needed
   ```

3. **Build and start the service:**
   ```bash
   docker-compose up -d --build
   ```

4. **Verify service is running:**
   ```bash
   curl http://localhost:2025/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "pandoc_version": "3.x.x",
     "timestamp": "2024-..."
   }
   ```

### Running Locally (Development)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Pandoc:**
   - macOS: `brew install pandoc`
   - Ubuntu: `sudo apt-get install pandoc`
   - Windows: Download from https://pandoc.org/installing.html

3. **Create reference template (optional):**
   ```bash
   pip install python-docx
   python create_reference_template.py
   ```

4. **Run the service:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## API Documentation

### Authentication

All conversion endpoints require an API key passed via the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

#### GET /health

Health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "pandoc_version": "3.1.2",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### POST /api/v1/convert/docx

Convert markdown content to DOCX format.

**Headers:**
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "# Hello World\n\nThis is **bold** text.",
  "filename": "my-document.docx"
}
```

**Response:**
- **200 OK**: Binary DOCX file
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing or invalid API key
- **500 Internal Server Error**: Conversion failed

**Example using curl:**
```bash
curl -X POST http://localhost:2025/api/v1/convert/docx \
  -H "Authorization: Bearer dev-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Sample Document\n\nThis is a **test** document with:\n\n- Bullet points\n- More items\n\n## Subsection\n\nAnd a [link](https://example.com).",
    "filename": "sample.docx"
  }' \
  --output sample.docx
```

### Testing with Sample Markdown

```bash
# Create a test file
cat > test.json << 'EOF'
{
  "content": "# Q4 Product Roadmap\n\n## Overview\n\nThis document outlines our plans.\n\n| Feature | Status | Owner |\n|---------|--------|-------|\n| Dashboard | In Progress | Alice |\n| API v3 | Planned | Bob |\n\n**Note:** All features are subject to change.",
  "filename": "roadmap.docx"
}
EOF

# Convert to DOCX
curl -X POST http://localhost:2025/api/v1/convert/docx \
  -H "Authorization: Bearer dev-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d @test.json \
  --output roadmap.docx

# Open the file
open roadmap.docx  # macOS
# xdg-open roadmap.docx  # Linux
# start roadmap.docx  # Windows
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EXPORT_SERVICE_API_KEY` | API key for authentication | `dev-secret-key-12345` |
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |
| `MAX_CONTENT_SIZE_MB` | Maximum markdown content size in MB | `5` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:3000,http://localhost:3001,...` |

## Docker Commands

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f document-service

# Stop the service
docker-compose down

# Restart the service
docker-compose restart

# Remove everything (including volumes)
docker-compose down -v
```

## Monitoring

### Check Service Status
```bash
docker-compose ps
```

### View Live Logs
```bash
docker-compose logs -f document-service
```

### Check Resource Usage
```bash
docker stats document-service
```

## Troubleshooting

### Service Won't Start

1. **Check if port 2025 is already in use:**
   ```bash
   lsof -i :2025
   ```

2. **View container logs:**
   ```bash
   docker-compose logs document-service
   ```

3. **Verify environment variables:**
   ```bash
   docker-compose config
   ```

### Conversion Fails

1. **Check Pandoc is installed in container:**
   ```bash
   docker-compose exec document-service pandoc --version
   ```

2. **Test conversion locally:**
   ```bash
   docker-compose exec document-service python -c "from app.converter import convert_markdown_to_docx; print(len(convert_markdown_to_docx('# Test')))"
   ```

3. **Review structured logs:**
   ```bash
   docker-compose logs document-service | grep -i error
   ```

### Authentication Issues

Verify your API key matches in both:
- `document-service/.env` → `EXPORT_SERVICE_API_KEY`
- `tasks-ai-app/.env.local` → `EXPORT_SERVICE_API_KEY`

### CORS Errors

Add your Next.js port to `ALLOWED_ORIGINS` in `.env`:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003
```

## Development

### Project Structure

```
document-service/
├── app/
│   ├── main.py          # FastAPI application
│   ├── converter.py     # Pandoc conversion logic
│   ├── models.py        # Pydantic models
│   └── config.py        # Configuration
├── templates/
│   └── reference.docx   # DOCX styling template
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
├── docker-compose.yml  # Service orchestration
├── .env               # Environment variables
└── README.md          # This file
```

### Adding New Features

1. Update models in `app/models.py`
2. Implement logic in appropriate module
3. Add endpoint to `app/main.py`
4. Update this README

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (create test files as needed)
pytest tests/
```

## Security Considerations

- API key authentication required for all conversions
- Content size limited to prevent DoS attacks
- Container runs as non-root user
- Resource limits enforced (512MB memory, 1 CPU)
- Input sanitization removes script tags
- CORS restricted to configured origins

## Performance

- Typical conversion time: <3 seconds for 5-page document
- Maximum content size: 5MB
- Conversion timeout: 30 seconds
- Memory limit: 512MB
- CPU limit: 1 core

## License

MIT

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs -f`
3. Verify Pandoc version compatibility
4. Create an issue in the project repository
