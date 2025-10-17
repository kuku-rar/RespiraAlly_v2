# RespiraAlly Backend

FastAPI-based backend service for RespiraAlly V2.0 - COPD Patient Healthcare Platform.

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ with pgvector extension
- **ORM**: SQLAlchemy 2.0+
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **AI/ML**: OpenAI API, LangChain

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── src/
│   └── respira_ally/
│       ├── api/          # API endpoints (Presentation Layer)
│       ├── application/  # Use cases (Application Layer)
│       ├── core/         # Core utilities
│       ├── domain/       # Domain models (Domain Layer)
│       └── infrastructure/ # External integrations (Infrastructure Layer)
├── tests/                # Test suite
└── pyproject.toml        # Dependencies and configuration
```

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry
- Docker & Docker Compose (for local development)

### Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Copy environment file
cp ../.env.example ../.env

# Edit .env with your configuration
```

### Database Setup

```bash
# Start PostgreSQL, Redis, RabbitMQ via Docker Compose (from project root)
cd ..
docker-compose up -d postgres redis rabbitmq

# Run migrations
cd backend
poetry run alembic upgrade head
```

### Running the Application

```bash
# Development mode with auto-reload
poetry run uvicorn respira_ally.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Testing

```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_auth.py

# Run with verbose output
poetry run pytest -v
```

### Code Quality

```bash
# Format code
poetry run black src tests

# Lint code
poetry run ruff check src tests

# Type checking
poetry run mypy src
```

## API Endpoints

- **Authentication**: `/api/v1/auth/`
- **Patients**: `/api/v1/patients/`
- **Daily Logs**: `/api/v1/daily-logs/`
- **Questionnaires**: `/api/v1/questionnaires/`
- **Risk Assessment**: `/api/v1/risk-assessment/`
- **Notifications**: `/api/v1/notifications/`
- **AI Voice**: `/api/v1/ai-voice/`

## Environment Variables

See `../.env.example` for all required environment variables.

## Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Run tests: `poetry run pytest`
4. Format and lint: `poetry run black . && poetry run ruff check .`
5. Commit with conventional commits: `git commit -m "feat(api): add new endpoint"`
6. Push and create PR

## Architecture

This project follows Clean Architecture principles with four main layers:

1. **Presentation Layer** (`api/`): HTTP endpoints, request/response handling
2. **Application Layer** (`application/`): Use cases, business workflows
3. **Domain Layer** (`domain/`): Core business logic, entities, value objects
4. **Infrastructure Layer** (`infrastructure/`): External services, databases, message queues

## License

MIT
