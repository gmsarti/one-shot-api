# One-Shot API

A FastAPI-based service that generates one-shot RPG stories using OpenAI's GPT models and stores them in a PostgreSQL database.

## Features

- Generate one-shot RPG stories with customizable parameters:
  - RPG System (e.g., D&D 5e)
  - Story Length
  - Theme
  - Player Count
  - Complexity
- Automatic keyword extraction from generated stories
- PostgreSQL database integration for story storage
- RESTful API endpoints for story generation and retrieval
- Swagger/OpenAPI documentation
- Docker support for easy deployment
- Health monitoring endpoints

## Prerequisites

- Python 3.8+ or Docker
- PostgreSQL (if running locally)
- OpenAI API key

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/one-shot-api.git
cd one-shot-api
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
```bash
createuser -s postgres
createdb -O postgres one_shot_api
```

5. Create a `.env` file with your configuration:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
DEBUG=True

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=one_shot_api

# Story Generation Parameters
DEFAULT_RPG_SYSTEM=D&D 5e
DEFAULT_STORY_LENGTH=medium
DEFAULT_THEME=fantasy
```

6. Run database migrations:
```bash
alembic upgrade head
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/one-shot-api.git
cd one-shot-api
```

2. Create a `.env` file as described above

3. Start the services using Docker Compose:
```bash
docker-compose up -d
```

## Usage

### API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Generating Stories

1. Start the API server:
```bash
# Local installation
python -m one_shot_api

# Docker installation
docker-compose up -d
```

2. Generate a story using the API:
```bash
curl -X POST http://localhost:8001/api/v1/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "rpg_system": "D&D 5e",
    "length": "medium",
    "theme": "fantasy",
    "player_count": 4,
    "complexity": 3
  }'
```

3. Retrieve a story by ID:
```bash
curl http://localhost:8001/api/v1/stories/{story_id}
```

### Health Monitoring

Check the service health:
```bash
curl http://localhost:8001/health
```

## API Documentation

### Base URL
All API endpoints are relative to the base URL:
```
http://localhost:8001/api/v1
```

### Authentication
Currently, the API does not require authentication. However, rate limiting is in place to prevent abuse.

### Rate Limiting
- Default rate limit: 100 requests per minute per IP address
- Rate limit headers:
  - `X-RateLimit-Limit`: Maximum number of requests per minute
  - `X-RateLimit-Remaining`: Number of requests remaining in the current window
  - `X-RateLimit-Reset`: Time when the rate limit will reset (UTC timestamp)

### Error Responses

All error responses follow this format:
```json
{
    "detail": "Error message description",
    "status_code": 400
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Service temporarily unavailable

### Endpoints

#### 1. Generate Story
```http
POST /stories/generate
```

Generates a new RPG one-shot story based on the provided parameters.

**Request Body:**
```json
{
    "rpg_system": "D&D 5e",
    "length": "medium",
    "theme": "fantasy",
    "player_count": 4,
    "complexity": 3
}
```

**Parameters:**
- `rpg_system` (string, required): The RPG system (e.g., "D&D 5e", "Pathfinder")
- `length` (string, required): Story length ("short", "medium", "long")
- `theme` (string, required): Story theme (e.g., "fantasy", "sci-fi", "horror")
- `player_count` (integer, required): Number of players (1-6)
- `complexity` (integer, required): Story complexity (1-5)

**Success Response:**
```json
{
    "title": "The Lost Temple of Eldara",
    "summary": "A group of adventurers discovers an ancient temple...",
    "plot_points": [
        "The party arrives at the village of Eldara",
        "They learn about the missing villagers",
        "The temple is discovered in the nearby forest"
    ],
    "characters": [
        "Villager Elder",
        "Temple Guardian",
        "Ancient Spirit"
    ],
    "locations": [
        "Village of Eldara",
        "Ancient Temple",
        "Forest Path"
    ],
    "items": [
        "Sacred Amulet",
        "Ancient Scroll",
        "Guardian's Key"
    ],
    "estimated_duration": "3-4 hours"
}
```

**Error Response Examples:**
```json
// Invalid parameters
{
    "detail": "Invalid RPG system: 'Invalid System'",
    "status_code": 400
}

// Rate limit exceeded
{
    "detail": "Rate limit exceeded. Please try again in 60 seconds.",
    "status_code": 429
}

// OpenAI API error
{
    "detail": "Failed to generate story: OpenAI API error",
    "status_code": 500
}
```

#### 2. Get Story
```http
GET /stories/{story_id}
```

Retrieves a previously generated story by its ID.

**Path Parameters:**
- `story_id` (integer, required): The ID of the story to retrieve

**Success Response:**
```json
{
    "title": "The Lost Temple of Eldara",
    "summary": "A group of adventurers discovers an ancient temple...",
    "plot_points": [
        "The party arrives at the village of Eldara",
        "They learn about the missing villagers",
        "The temple is discovered in the nearby forest"
    ],
    "characters": [
        "Villager Elder",
        "Temple Guardian",
        "Ancient Spirit"
    ],
    "locations": [
        "Village of Eldara",
        "Ancient Temple",
        "Forest Path"
    ],
    "items": [
        "Sacred Amulet",
        "Ancient Scroll",
        "Guardian's Key"
    ],
    "estimated_duration": "3-4 hours"
}
```

**Error Response Examples:**
```json
// Story not found
{
    "detail": "Story not found",
    "status_code": 404
}

// Invalid story ID
{
    "detail": "Invalid story ID format",
    "status_code": 400
}
```

#### 3. Health Check
```http
GET /health
```

Checks the health status of the service and its dependencies.

**Success Response:**
```json
{
    "status": "healthy",
    "version": "0.1.0",
    "database": {
        "status": "healthy"
    },
    "system": {
        "memory": {
            "total": 8589934592,
            "available": 4294967296,
            "used": 4294967296,
            "percent": 50.0
        },
        "disk": {
            "total": 107374182400,
            "used": 53687091200,
            "free": 53687091200,
            "percent": 50.0
        }
    }
}
```

**Error Response Examples:**
```json
// Database connection error
{
    "status": "unhealthy",
    "version": "0.1.0",
    "database": {
        "status": "unhealthy: Connection refused"
    },
    "system": {
        "memory": {
            "total": 8589934592,
            "available": 4294967296,
            "used": 4294967296,
            "percent": 50.0
        },
        "disk": {
            "total": 107374182400,
            "used": 53687091200,
            "free": 53687091200,
            "percent": 50.0
        }
    }
}
```

### Best Practices

1. **Error Handling**
   - Always check the response status code
   - Implement exponential backoff for rate limit errors
   - Handle network errors gracefully

2. **Performance**
   - Cache story responses when possible
   - Implement request batching for multiple stories
   - Use compression for large responses

3. **Security**
   - Validate all input parameters
   - Sanitize story content before display
   - Implement proper CORS policies

4. **Monitoring**
   - Monitor API response times
   - Track error rates
   - Set up alerts for service health

### SDK Examples

#### Python
```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

def generate_story(rpg_system, length, theme, player_count, complexity):
    response = requests.post(
        f"{BASE_URL}/stories/generate",
        json={
            "rpg_system": rpg_system,
            "length": length,
            "theme": theme,
            "player_count": player_count,
            "complexity": complexity
        }
    )
    response.raise_for_status()
    return response.json()

def get_story(story_id):
    response = requests.get(f"{BASE_URL}/stories/{story_id}")
    response.raise_for_status()
    return response.json()
```

#### JavaScript/Node.js
```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';

async function generateStory(rpgSystem, length, theme, playerCount, complexity) {
    const response = await axios.post(`${BASE_URL}/stories/generate`, {
        rpg_system: rpgSystem,
        length: length,
        theme: theme,
        player_count: playerCount,
        complexity: complexity
    });
    return response.data;
}

async function getStory(storyId) {
    const response = await axios.get(`${BASE_URL}/stories/${storyId}`);
    return response.data;
}
```

## Project Structure

```
one-shot-api/
├── alembic/              # Database migrations
├── src/
│   └── one_shot_api/
│       ├── agents/       # Story generation logic
│       ├── api/          # FastAPI routes
│       ├── config/       # Configuration management
│       ├── core/         # Core functionality
│       ├── models/       # Database and request models
│       ├── schemas/      # Pydantic models
│       ├── services/     # Business logic
│       └── utils/        # Utility functions
├── tests/               # Test suite
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── alembic.ini         # Alembic configuration
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Docker build configuration
├── pyproject.toml      # Project configuration
└── README.md          # Project documentation
```

## Development

### Development Mode Setup

1. Clone the repository and set up your environment:
```bash
git clone https://github.com/yourusername/one-shot-api.git
cd one-shot-api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

4. Create a `.env` file with development settings:
```env
# Development-specific settings
DEBUG=True
LOG_LEVEL=DEBUG
LOG_JSON_FORMAT=False

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Database Configuration (Development)
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=one_shot_api_dev

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

5. Start the development server with hot-reload:
```bash
uvicorn one_shot_api.main:app --reload --host 0.0.0.0 --port 8001
```

### Docker Development

For development with Docker, you can use the following commands:

1. Build the development image:
```bash
docker-compose -f docker-compose.dev.yml build
```

2. Start the development environment:
```bash
docker-compose -f docker-compose.dev.yml up
```

This will:
- Mount your local source code into the container
- Enable hot-reload for code changes
- Set up a development database
- Configure development logging

3. Access the development services:
- API: http://localhost:8001
- Database: localhost:5432
- Adminer (Database UI): http://localhost:8080

### Running Tests

```bash
# Local installation
pytest

# Docker installation
docker-compose run --rm api pytest
```

### Code Quality

The project uses several tools for code quality:
- `ruff` for linting
- `black` for code formatting
- `mypy` for type checking
- `pre-commit` for git hooks

Run all checks:
```bash
# Local installation
pre-commit run --all-files

# Docker installation
docker-compose run --rm api pre-commit run --all-files
```

### Debugging

1. Using VS Code:
   - Install the Python and Docker extensions
   - Use the provided launch configurations in `.vscode/launch.json`
   - Set breakpoints in your code
   - Press F5 to start debugging

2. Using Docker:
   - Attach to the running container:
   ```bash
   docker-compose -f docker-compose.dev.yml exec api bash
   ```
   - View logs:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f api
   ```

### Database Management

1. Run migrations:
```bash
# Local
alembic upgrade head

# Docker
docker-compose -f docker-compose.dev.yml exec api alembic upgrade head
```

2. Create a new migration:
```bash
# Local
alembic revision --autogenerate -m "description"

# Docker
docker-compose -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "description"
```

3. Reset the database (development only):
```bash
# Local
alembic downgrade base && alembic upgrade head

# Docker
docker-compose -f docker-compose.dev.yml exec api alembic downgrade base && alembic upgrade head
```
