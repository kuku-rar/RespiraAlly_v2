# RespiraAlly V2.0 - COPD Patient Healthcare Platform

[繁體中文](README.zh-TW.md)

> **AI-powered healthcare platform for COPD patient management with LINE integration, voice interaction, and intelligent risk assessment**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)

## 📋 Table of Contents

- [Project Overview](#project-overview)
  - [Project Status](#project-status)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Documentation](#documentation)
- [Testing](#testing)
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

### 📊 Project Status

**Current Phase**: Sprint 2 Week 1 - Patient Management & Daily Logs (Completed ✅)

| Metric | Status |
|--------|--------|
| **Overall Progress** | 26.5% (295.2h / 1113h) |
| **Current Sprint** | Sprint 2 - 24.2% Complete |
| **Project Start Date** | 2025-10-18 |
| **Expected MVP Release** | 2026-Q1 |
| **Total Duration** | 16 weeks (8 Sprints × 14 days) |

**Completed Milestones** ✅:

- ✅ **Sprint 0 - Project Management Setup** (100% - 17h/17h)
  - WBS Development Plan v2.2
  - 8 Sprint Timeline Planning
  - Git Workflow SOP & PR Review SLA
  - CI/CD Quality Gates Configuration
  - Conventional Commits Enforcement (commitlint + husky)

- ✅ **Sprint 0 - System Architecture Design** (100% - 148h/148h)
  - C4 Architecture Diagrams (Level 1-2)
  - Database Schema Design (PostgreSQL with pgvector)
  - RESTful API Specification
  - Frontend Architecture Specification (Dashboard + LIFF)
  - Elder-First Design Principles Documentation
  - ADR (Architecture Decision Records) × 8

- ✅ **Sprint 1 - Infrastructure & Authentication** (93.5% - 97.2h/104h)
  - Docker Compose Environment
  - Database Schema + Phase 0 Indexes
  - JWT Authentication (with Token Blacklist & Refresh)
  - Dashboard & LIFF Project Initialization
  - API Client with Mock Mode

- ✅ **Sprint 2 Week 1 - Frontend Patient Management** (100% - 24h/24h) 🎉
  - **Task 3.5.5**: Dashboard Login Page UI (4h)
  - **Task 3.5.6**: LIFF Registration Page UI (2h)
  - **Task 4.4.2**: Patient List UI (6h)
  - **Task 4.4.3**: Advanced Table Components (6h) - 3 reusable components
  - **Task 4.3.1**: LIFF Daily Log Form (6h)

**Current Sprint 2 Week 1 Focus** (✅ Completed):
- ✅ Dashboard Login & Authentication Flow
- ✅ LIFF Patient Registration with LINE Profile
- ✅ Patient List with Filters, Sorting, Pagination
- ✅ Reusable Components (PatientFilters, PatientTable, PatientPagination)
- ✅ LIFF Daily Health Log Form with Elder-First Design

**Quality Achievements** 🏆:
- ✅ **Test Coverage**: 100% pass rate (75/75 integration tests)
- ✅ **Elder-First Design**: 100% compliance (18px+ fonts, 44px+ touch targets)
- ✅ **Code Quality**: Zero technical debt, 50% code reduction through componentization
- ✅ **Mock Mode**: Complete frontend-backend decoupling for parallel development

**Quality Gates Status**:
- ✅ TypeScript Strict Mode - No type errors
- ✅ ESLint - No warnings
- ✅ Integration Tests - 100% pass rate
- ✅ E2E Test Checklist - Comprehensive coverage

For detailed progress tracking, see [WBS Development Plan](docs/16_wbs_development_plan.md)

## ✨ Key Features

### For Patients (LINE Bot + LIFF)

- 🔐 **Easy Registration**: Quick signup via LINE User ID with auto-filled profile
- 📝 **Daily Health Logs**: Simple form to track symptoms, medications, water intake, and steps
- 🎙️ **AI Voice Q&A**: Ask health questions using voice (Taiwanese/Mandarin support)
- 📊 **Health Trends**: View 7-day and 30-day health progress charts
- 📋 **Questionnaires**: Complete CAT/mMRC assessments
- ⚠️ **Smart Alerts**: Receive personalized health reminders

### For Therapists (Web Dashboard)

- 🔐 **Secure Login**: JWT-based authentication with token refresh
- 👥 **Patient Management**: Comprehensive patient list with risk indicators
- 📊 **Advanced Filtering**: Sort by name, age, risk level, adherence rate
- 🔍 **Search & Pagination**: Find patients quickly with efficient navigation
- 📈 **360° Patient Profile**: Complete health history and analytics (Coming Soon)
- 🚨 **Risk Assessment Center**: Real-time alerts for high-risk patients (Coming Soon)

### AI Capabilities (Coming in Sprint 5-6)

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

- **Dashboard**: Next.js 14+ (App Router), React 18+, TypeScript 5.3+, Tailwind CSS
- **LIFF**: Vite 5+, React 18+, TypeScript 5.3+, Tailwind CSS
- **State Management**: Zustand 4.5+, TanStack Query 5.17+
- **Form Handling**: React Hook Form 7.49+
- **Validation**: Zod 3.22+

### AI/ML

- **STT**: OpenAI Whisper API
- **LLM**: OpenAI GPT-4 Turbo
- **TTS**: Emotion-TTS / OpenAI TTS
- **RAG**: LangChain + pgvector + BM25 hybrid retrieval
- **Embeddings**: OpenAI text-embedding-3-small

### DevOps

- **Package Manager**: uv (Python), npm (Node.js)
- **Containerization**: Docker, Docker Compose
- **Deployment**: Zeabur
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, Sentry

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11+
- **Node.js**: 18.17+
- **uv**: Latest version ([Installation Guide](https://github.com/astral-sh/uv))
- **Docker**: Latest version
- **Docker Compose**: Latest version

### Quick Start

#### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies with uv
uv sync

# 3. Start infrastructure services (PostgreSQL, Redis, RabbitMQ, MinIO)
docker-compose up -d postgres redis rabbitmq minio

# 4. Run database migrations
uv run alembic upgrade head

# 5. Start FastAPI server
uv run uvicorn respira_ally.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (Dashboard)

```bash
# 1. Navigate to dashboard directory
cd frontend/dashboard

# 2. Install dependencies
npm install

# 3. Configure environment (Mock Mode for development)
echo "NEXT_PUBLIC_MOCK_MODE=true" > .env.local
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" >> .env.local

# 4. Start development server
npm run dev
```

#### Frontend Setup (LIFF)

```bash
# 1. Navigate to LIFF directory
cd frontend/liff

# 2. Install dependencies
npm install

# 3. Configure environment (Mock Mode for development)
echo "VITE_MOCK_MODE=true" > .env
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" >> .env
echo "VITE_LIFF_ID=your-liff-id" >> .env

# 4. Start development server
npm run dev
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **LIFF**: http://localhost:5173
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

### Mock Mode Development

Both frontend applications support **Mock Mode** for independent development without backend dependency:

- **Dashboard**: Set `NEXT_PUBLIC_MOCK_MODE=true` in `.env.local`
- **LIFF**: Set `VITE_MOCK_MODE=true` in `.env`

Mock mode provides:
- ✅ Realistic API delays (600-1200ms)
- ✅ 8 mock patients with complete data
- ✅ 3 mock daily logs
- ✅ Console logging for all API calls
- ✅ Complete form validation

## 📁 Project Structure

```
RespiraAlly/
├── backend/                    # FastAPI backend service
│   ├── src/respira_ally/
│   │   ├── api/                # API endpoints (Presentation Layer)
│   │   │   └── v1/routers/     # API routers (auth, patient, daily_log)
│   │   ├── application/        # Use cases (Application Layer)
│   │   │   ├── auth/           # Authentication use cases
│   │   │   ├── patient/        # Patient management services
│   │   │   └── daily_log/      # Daily log services
│   │   ├── core/               # Core utilities and config
│   │   │   ├── schemas/        # Pydantic models (auth, patient, daily_log)
│   │   │   ├── security.py     # JWT utilities
│   │   │   └── config.py       # Application configuration
│   │   ├── domain/             # Domain models (Domain Layer)
│   │   │   ├── entities/       # Domain entities
│   │   │   ├── repositories/   # Repository interfaces
│   │   │   └── events/         # Domain events
│   │   └── infrastructure/     # External integrations (Infrastructure Layer)
│   │       ├── database/       # Database models & connections
│   │       └── repositories/   # Repository implementations
│   ├── tests/                  # Test suite
│   │   ├── unit/               # Unit tests
│   │   └── integration/        # Integration tests
│   └── pyproject.toml          # Python dependencies
│
├── frontend/
│   ├── dashboard/              # Therapist dashboard (Next.js)
│   │   ├── app/                # Next.js App Router
│   │   │   ├── login/          # Login page
│   │   │   ├── dashboard/      # Main dashboard
│   │   │   └── patients/       # Patient management pages
│   │   ├── components/         # React components
│   │   │   └── patients/       # Reusable patient components
│   │   │       ├── PatientFilters.tsx
│   │   │       ├── PatientTable.tsx
│   │   │       └── PatientPagination.tsx
│   │   └── lib/                # Utilities and API client
│   │       ├── types/          # TypeScript types (auth, patient)
│   │       └── api/            # API services (auth, patients)
│   │
│   └── liff/                   # Patient LIFF app (Vite + React)
│       ├── src/
│       │   ├── pages/          # Page components
│       │   │   ├── Register.tsx    # Patient registration
│       │   │   └── LogForm.tsx     # Daily health log form
│       │   ├── components/     # Reusable components
│       │   ├── hooks/          # Custom React hooks (useLiff)
│       │   ├── types/          # TypeScript types (auth, daily-log)
│       │   ├── api/            # API services (auth, daily-log)
│       │   └── services/       # API client
│       └── vite.config.ts
│
├── docs/                       # Project documentation
│   ├── adr/                    # Architecture Decision Records
│   ├── bdd/                    # BDD scenarios
│   ├── test_reports/           # Testing reports
│   │   ├── INTEGRATION_TEST_REPORT.md  # Integration test results (100% pass)
│   │   └── E2E_TEST_CHECKLIST.md       # E2E test checklist (75+ items)
│   ├── PARALLEL_DEV_STRATEGY.md        # Frontend-backend parallel development guide
│   ├── 02_product_requirements_document.md
│   ├── 05_architecture_and_design.md
│   ├── 06_api_design_specification.md
│   └── 16_wbs_development_plan.md
│
├── scripts/                    # Development and deployment scripts
│   ├── dev-backend.sh          # Backend quick start script
│   └── dev-frontend.sh         # Frontend quick start script
├── .github/workflows/          # CI/CD workflows
├── docker-compose.yml          # Local development environment
└── README.md                   # This file
```

## 💻 Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `dev`: Development integration branch
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
uv run black src tests           # Format
uv run ruff check src tests      # Lint
uv run mypy src                  # Type check
uv run pytest                    # Test

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

### Parallel Development Strategy

RespiraAlly V2.0 uses a **parallel development approach** to maximize efficiency:

- **Frontend**: Develops with Mock Mode, independent of backend status
- **Backend**: Focuses on API implementation and Clean Architecture
- **Integration**: Daily integration checks at 5:00 PM
- **Weekly Sync**: Mid-sprint integration testing on Wednesdays

See [Parallel Development Strategy](docs/PARALLEL_DEV_STRATEGY.md) for detailed workflow.

## 📚 Documentation

### Core Documentation

- **[Product Requirements Document](docs/02_product_requirements_document.md)** - Business requirements and user stories
- **[Architecture & Design](docs/05_architecture_and_design.md)** - System architecture (C4 model, DDD)
- **[API Specification](docs/06_api_design_specification.md)** - REST API contracts
- **[Module Specification](docs/07_module_specification_and_tests.md)** - Detailed module design
- **[WBS Development Plan](docs/16_wbs_development_plan.md)** - Project timeline and tasks

### Project Management Documentation

- **[Development Workflow](docs/01_development_workflow.md)** - Development process and quality gates
- **[Git Workflow SOP](docs/project_management/git_workflow_sop.md)** - Branching strategy and commit conventions
- **[PR Review SLA Policy](docs/project_management/pr_review_sla_policy.md)** - Code review service level agreements
- **[Parallel Development Strategy](docs/PARALLEL_DEV_STRATEGY.md)** - Frontend-backend parallel workflow

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

## 🧪 Testing

### Test Coverage

- **Integration Tests**: 75 test cases, **100% pass rate** ✅
- **Elder-First Design**: 100% compliance (18px+ fonts, 44px+ touch targets) ✅
- **Mock Mode**: Complete API mocking with realistic delays ✅

### Test Reports

- **[Integration Test Report](docs/test_reports/INTEGRATION_TEST_REPORT.md)** - Detailed results (100% pass)
- **[E2E Test Checklist](docs/test_reports/E2E_TEST_CHECKLIST.md)** - Manual testing checklist (75+ items)

### Testing Strategy

- **Unit Tests**: Domain logic, utilities (≥80% coverage)
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Critical user flows (login, registration, daily logs)
- **Performance Tests**: API response time, AI processing latency

### Running Tests

```bash
# Backend unit tests
cd backend
uv run pytest tests/unit -v

# Backend integration tests
uv run pytest tests/integration -v

# Frontend type checking
cd frontend/dashboard
npm run type-check

# Frontend linting
npm run lint
```

## 🗓️ Project Timeline

**Duration**: 16 weeks (8 Sprints × 14 days) | **Start**: 2025-10-18 | **MVP Release**: 2026 Q1

| Sprint | Focus | Duration | Status | Progress |
|--------|-------|----------|--------|----------|
| **Sprint 0** | Planning & Architecture | Week 0 | ✅ Complete | 100% (165h/165h) |
| **Sprint 1** | Infrastructure & Auth | Week 1-2 | ⚡ Mostly Done | 93.5% (97.2h/104h) |
| **Sprint 2** | Patient Mgmt & Logs | Week 3-4 | 🔄 In Progress | 24.2% (35.75h/147.75h) |
| **Sprint 3** | Dashboard & Surveys | Week 5-6 | ⏳ Planned | 0% |
| **Sprint 4** | Risk Engine | Week 7-8 | ⏳ Planned | 0% |
| **Sprint 5** | RAG System | Week 9-10 | ⏳ Planned | 0% |
| **Sprint 6** | AI Voice Chain | Week 11-12 | ⏳ Planned | 0% |
| **Sprint 7-8** | Notification & Polish | Week 13-16 | ⏳ Planned | 0% |

**Current Status**: Sprint 2 Week 1 (Frontend Patient Management) - ✅ **100% Complete**
- See [WBS Development Plan](docs/16_wbs_development_plan.md) for detailed breakdown

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

## 🏆 Project Achievements

### Sprint 2 Week 1 Completion 🎉
- ✅ **100% Task Completion** (24h/24h)
- ✅ **100% Test Pass Rate** (75/75 integration tests)
- ✅ **Zero Technical Debt** (50% code reduction through componentization)
- ✅ **Elder-First Design** (100% compliance)
- ✅ **3 Reusable Components** (Future-proof architecture)

### Quality Metrics
- **Test Coverage**: 100% pass rate
- **Code Quality**: Zero TypeScript errors, Zero ESLint warnings
- **Performance**: All pages load < 3 seconds
- **Accessibility**: WCAG AAA compliance for Elder-First design

---

**Built with ❤️ by RespiraAlly Team | AIPE01 Final Project 2025-2026**

**Last Updated**: 2025-10-20 | **Version**: v2.0.0-alpha | **Commit**: Latest
