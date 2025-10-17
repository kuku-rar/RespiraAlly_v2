# RespiraAlly V2.0 - COPD Patient Healthcare Platform

> **AI-powered healthcare platform for COPD patient management with LINE integration, voice interaction, and intelligent risk assessment**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

RespiraAlly V2.0 is an innovative digital health management platform designed to support COPD (Chronic Obstructive Pulmonary Disease) patients and their healthcare providers. The platform combines intelligent reminders, AI voice interaction, real-time risk assessment, and comprehensive patient dashboards to transform passive treatment into proactive prevention.

### Business Goals

- **Patient Empowerment**: Provide accessible, personalized health management tools via LINE
- **Healthcare Efficiency**: Enable therapists to manage multiple patients effectively
- **Preventive Care**: Identify health risks early through AI-powered analysis
- **Behavior Change**: Achieve ≥75% health behavior adherence rate

### Success Metrics

- **North Star Metric**: Health Behavior Adherence Rate ≥ 75%
- Patient D30 retention rate
- Therapist weekly login frequency
- AI response accuracy ≥ 85%

## ✨ Key Features

### For Patients (LINE Bot + LIFF)

- 🔐 **Easy Registration**: Quick signup via LINE User ID
- 📝 **Daily Health Logs**: Simple form to track symptoms, medications, and activities
- 🎙️ **AI Voice Q&A**: Ask health questions using voice (Taiwanese/Mandarin support)
- 📊 **Health Trends**: View 7-day and 30-day health progress charts
- 📋 **Questionnaires**: Complete CAT/mMRC assessments
- ⚠️ **Smart Alerts**: Receive personalized health reminders

### For Therapists (Web Dashboard)

- 👥 **Patient Management**: Comprehensive patient list with risk indicators
- 📈 **360° Patient Profile**: Complete health history and analytics
- 🚨 **Risk Assessment Center**: Real-time alerts for high-risk patients
- 📅 **Task Management**: Assign and track patient follow-up tasks
- 📊 **Analytics Dashboard**: Population health trends and insights

### AI Capabilities

- 🧠 **RAG System**: Retrieve-Augmented Generation with medical knowledge base
- 🎤 **Speech-to-Text**: Whisper-based STT for voice input
- 💬 **LLM Processing**: GPT-4 powered intelligent responses
- 🔊 **Text-to-Speech**: Natural voice synthesis for responses
- 📖 **Source Citation**: Transparent AI reasoning with references

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     LINE Platform                       │
│  ┌──────────────┐                    ┌──────────────┐  │
│  │  Messaging   │                    │     LIFF     │  │
│  │     API      │                    │  (React)     │  │
│  └──────┬───────┘                    └──────┬───────┘  │
└─────────┼────────────────────────────────────┼──────────┘
          │                                    │
          │    ┌─────────────────────────────┐ │
          │    │      API Gateway            │ │
          │    │     (FastAPI)               │ │
          └────┤                             ├─┘
               └──────────┬──────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼───────┐      ┌─────▼─────┐      ┌───────▼───────┐
│  Patient  │      │   Auth    │      │   Dashboard   │
│  Service  │      │  Service  │      │ (Next.js)     │
└───────────┘      └───────────┘      └───────────────┘
    │                     │
    │              ┌──────▼──────┐
    │              │ Risk Engine │
    │              └─────────────┘
    │
┌───▼────────────────────────────────────┐
│        AI Worker (Async)               │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌────┐ │
│  │ STT  ├──► LLM  ├──► TTS  ├──►WS  │ │
│  └──────┘  └──────┘  └──────┘  └────┘ │
└────────────────────────────────────────┘
```

### Technology Layers

1. **Presentation Layer**: LINE Bot, LIFF, Next.js Dashboard
2. **Application Layer**: FastAPI use cases and business workflows
3. **Domain Layer**: Core business logic (Clean Architecture)
4. **Infrastructure Layer**: PostgreSQL, Redis, RabbitMQ, MongoDB

## 🛠️ Tech Stack

### Backend

- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 15+ with pgvector
- **Cache**: Redis 7+
- **Message Queue**: RabbitMQ 3+
- **Event Store**: MongoDB 7+

### Frontend

- **Dashboard**: Next.js 14+ (App Router), React 18+, TypeScript, Tailwind CSS
- **LIFF**: Vite, React 18+, TypeScript, Tailwind CSS
- **State Management**: Zustand, TanStack Query

### AI/ML

- **STT**: OpenAI Whisper API
- **LLM**: OpenAI GPT-4 Turbo
- **TTS**: Emotion-TTS / OpenAI TTS
- **RAG**: LangChain + pgvector + BM25 hybrid retrieval
- **Embeddings**: OpenAI text-embedding-3-small

### DevOps

- **Containerization**: Docker, Docker Compose
- **Deployment**: Zeabur
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, Sentry

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11+
- **Node.js**: 18.17+
- **Poetry**: Latest version
- **Docker**: Latest version
- **Docker Compose**: Latest version

### Quick Start

1. **Clone the repository**

```bash
git clone <repository-url>
cd RespiraAlly
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start infrastructure services**

```bash
# Start PostgreSQL, Redis, RabbitMQ, MongoDB
docker-compose up -d
```

4. **Set up backend**

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn respira_ally.main:app --reload
```

5. **Set up frontend (Dashboard)**

```bash
cd frontend/dashboard
npm install
npm run dev
```

6. **Set up frontend (LIFF)**

```bash
cd frontend/liff
npm install
npm run dev
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **LIFF**: http://localhost:5173
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 📁 Project Structure

```
RespiraAlly/
├── backend/                    # FastAPI backend service
│   ├── src/respira_ally/
│   │   ├── api/                # API endpoints (Presentation Layer)
│   │   ├── application/        # Use cases (Application Layer)
│   │   ├── core/               # Core utilities and config
│   │   ├── domain/             # Domain models (Domain Layer)
│   │   └── infrastructure/     # External integrations (Infrastructure Layer)
│   ├── tests/                  # Test suite
│   └── pyproject.toml          # Python dependencies
│
├── frontend/
│   ├── dashboard/              # Therapist dashboard (Next.js)
│   │   ├── app/                # Next.js App Router
│   │   ├── components/         # React components
│   │   └── lib/                # Utilities and API client
│   │
│   └── liff/                   # Patient LIFF app (Vite + React)
│       ├── src/
│       │   ├── pages/          # Page components
│       │   ├── components/     # Reusable components
│       │   └── services/       # API services
│       └── vite.config.ts
│
├── docs/                       # Project documentation
│   ├── adr/                    # Architecture Decision Records
│   ├── bdd/                    # BDD scenarios
│   ├── 02_product_requirements_document.md
│   ├── 05_architecture_and_design.md
│   ├── 06_api_design_specification.md
│   └── WBS_DEVELOPMENT_PLAN.md
│
├── scripts/                    # Development and deployment scripts
├── .github/workflows/          # CI/CD workflows
├── docker-compose.yml          # Local development environment
└── README.md                   # This file
```

## 💻 Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Development integration branch
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches
- `hotfix/*`: Production hotfix branches

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(api): add patient registration endpoint
fix(liff): resolve voice recording issue
docs(readme): update installation instructions
refactor(domain): simplify risk calculation logic
test(auth): add JWT token validation tests
```

### Code Quality

```bash
# Backend
cd backend
poetry run black src tests           # Format
poetry run ruff check src tests      # Lint
poetry run mypy src                  # Type check
poetry run pytest                    # Test

# Frontend Dashboard
cd frontend/dashboard
npm run lint                         # Lint
npm run type-check                   # Type check
npm test                             # Test

# Frontend LIFF
cd frontend/liff
npm run lint                         # Lint
npm run type-check                   # Type check
```

### Testing Strategy

- **Unit Tests**: Domain logic, utilities (≥80% coverage)
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Critical user flows
- **Performance Tests**: API response time, AI processing latency

## 📚 Documentation

### Core Documentation

- **[Product Requirements Document](docs/02_product_requirements_document.md)** - Business requirements and user stories
- **[Architecture & Design](docs/05_architecture_and_design.md)** - System architecture (C4 model, DDD)
- **[API Specification](docs/06_api_design_specification.md)** - REST API contracts
- **[Module Specification](docs/07_module_specification_and_tests.md)** - Detailed module design
- **[WBS Development Plan](docs/WBS_DEVELOPMENT_PLAN.md)** - Project timeline and tasks

### Architecture Decision Records (ADR)

- [ADR-001: FastAPI vs Flask](docs/adr/ADR-001-fastapi-vs-flask.md)
- [ADR-002: pgvector for Vector DB](docs/adr/ADR-002-pgvector-for-vector-db.md)
- [ADR-003: MongoDB for Event Logs](docs/adr/ADR-003-mongodb-for-event-logs.md)
- [ADR-004: LINE as Patient Entrypoint](docs/adr/ADR-004-line-as-patient-entrypoint.md)
- [ADR-005: RabbitMQ for Message Queue](docs/adr/ADR-005-rabbitmq-for-message-queue.md)

### BDD Scenarios

- [Epic 100: Authentication](docs/bdd/epic_100_authentication.feature)
- [Epic 200: Daily Management](docs/bdd/epic_200_daily_management.feature)
- [Epic 300: AI Interaction](docs/bdd/epic_300_ai_interaction.feature)

## 🗓️ Project Timeline

- **Sprint 0**: Planning & Architecture (Week 0)
- **Sprint 1-2**: Infrastructure & Authentication (Week 1-4)
- **Sprint 3-4**: Core Features (Patient Management, Logs, Risk Engine) (Week 5-8)
- **Sprint 5-6**: AI Capabilities (RAG System, Voice Chain) (Week 9-12)
- **Sprint 7-8**: Polish & Deployment (Week 13-16)

**Target Release**: 2026 Q1

## 🤝 Contributing

This is an academic project for AIPE01 Final Project. Contributions are limited to project team members.

### Team Roles

- **Project Manager**: Sprint planning, progress tracking
- **Technical Lead**: Backend architecture, code review
- **Product Owner**: Requirements definition, acceptance criteria
- **System Architect**: C4 architecture, DDD strategy, ADR authoring
- **AI/ML Engineer**: RAG system, STT/LLM/TTS integration
- **Frontend Engineer**: React/Next.js, LIFF, Dashboard UI/UX
- **QA Engineer**: Test strategy, automation, quality assurance
- **DevOps Engineer**: CI/CD, deployment, monitoring

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- **LINE Platform**: For messaging and LIFF framework
- **OpenAI**: For AI/ML capabilities
- **FastAPI**: For modern Python web framework
- **Next.js**: For React framework
- **VibeCoding**: For enterprise workflow templates

---

**Built with ❤️ by RespiraAlly Team | AIPE01 Final Project 2025-2026**
