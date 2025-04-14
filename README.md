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

## Prerequisites

- Python 3.8+
- PostgreSQL
- OpenAI API key

## Installation

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

## Usage

1. Start the API server:
```bash
python -m one_shot_api
```

2. Generate a story:
```bash
curl -X POST http://localhost:8001/stories/generate \
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
curl http://localhost:8001/stories/{story_id}
```

## API Endpoints

- `POST /stories/generate`: Generate a new story
- `GET /stories/{story_id}`: Retrieve a story by ID

## Project Structure

```
one-shot-api/
├── alembic/              # Database migrations
├── src/
│   └── one_shot_api/
│       ├── agents/       # Story generation logic
│       ├── api/          # FastAPI routes
│       ├── models/       # Database and request models
│       └── utils/        # Utility functions
├── .env                  # Environment variables
├── .env.example          # Example environment variables
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## TODO List

### Priority 1: Essential Setup
- [X] Add comprehensive API documentation using Swagger/OpenAPI
- [X] Complete environment variables documentation in README
- [X] Add version pinning for all dependencies
- [X] Set up minimum test coverage requirements (80%)
- [X] Add proper error handling and HTTP responses
- [X] Configure structured logging

### Priority 2: Development Tools
- [ ] Add security scanning with `safety` for dependency checks
- [ ] Set up `git-secrets` for sensitive information prevention
- [ ] Add complexity checks using `radon`
- [ ] Add docstring validation with `darglint`
- [ ] Configure pre-commit hooks for all code quality tools

### Priority 3: Build and Deployment
- [ ] Add version management with `bump2version`
- [ ] Create `MANIFEST.in` for non-Python files
- [ ] Set up proper build configuration in `setup.py`
- [ ] Add database backup/restore procedures
- [ ] Create basic performance benchmarks

### Priority 4: Advanced Features
- [ ] Add containerization with Docker
- [ ] Create multi-stage Docker builds
- [ ] Add health checks
- [ ] Set up application metrics
- [ ] Add load testing scripts

### Priority 5: Documentation and Maintenance
- [ ] Add migration testing
- [ ] Create comprehensive development guide
- [ ] Add troubleshooting guide
- [ ] Create maintenance procedures
- [ ] Add performance optimization guide
