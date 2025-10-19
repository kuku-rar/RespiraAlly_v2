#!/bin/bash
# RespiraAlly Backend - Clean Architecture 目錄結構設置腳本
# 基於 05_architecture_and_design.md §4.1.1 與 10_class_relationships_and_module_design.md
# 遵循 7 個 Bounded Context 的模組劃分

set -euo pipefail

BACKEND_DIR="/mnt/a/AIPE01_期末專題/RespiraAlly/backend"
SRC_DIR="$BACKEND_DIR/src/respira_ally"

echo "🏗️  設置 Clean Architecture 目錄結構..."
echo "📋 基於 7 個 Bounded Context: auth, patient, daily_log, survey, risk, rag, notification"
echo ""

# ============================================
# Presentation Layer - API Routes
# ============================================
echo "📝 創建 Presentation Layer (API Routes)..."
mkdir -p "$SRC_DIR/api/v1/routers"
touch "$SRC_DIR/api/v1/routers/__init__.py"
touch "$SRC_DIR/api/v1/routers/auth.py"
touch "$SRC_DIR/api/v1/routers/patient.py"
touch "$SRC_DIR/api/v1/routers/daily_log.py"
touch "$SRC_DIR/api/v1/routers/survey.py"
touch "$SRC_DIR/api/v1/routers/risk.py"
touch "$SRC_DIR/api/v1/routers/rag.py"
touch "$SRC_DIR/api/v1/routers/notification.py"

# ============================================
# Application Layer - Use Cases by Bounded Context
# ============================================
echo "📦 創建 Application Layer (Use Cases by Bounded Context)..."

# 1. Auth Context (通用子域)
mkdir -p "$SRC_DIR/application/auth/use_cases"
mkdir -p "$SRC_DIR/application/auth/schemas"
touch "$SRC_DIR/application/auth/__init__.py"
touch "$SRC_DIR/application/auth/use_cases/__init__.py"
touch "$SRC_DIR/application/auth/use_cases/login_use_case.py"
touch "$SRC_DIR/application/auth/use_cases/register_use_case.py"
touch "$SRC_DIR/application/auth/use_cases/refresh_token_use_case.py"
touch "$SRC_DIR/application/auth/schemas/__init__.py"
touch "$SRC_DIR/application/auth/schemas/auth_schemas.py"

# 2. Patient Context (支撐子域)
mkdir -p "$SRC_DIR/application/patient/use_cases"
mkdir -p "$SRC_DIR/application/patient/schemas"
touch "$SRC_DIR/application/patient/__init__.py"
touch "$SRC_DIR/application/patient/use_cases/__init__.py"
touch "$SRC_DIR/application/patient/use_cases/create_patient_use_case.py"
touch "$SRC_DIR/application/patient/use_cases/update_patient_use_case.py"
touch "$SRC_DIR/application/patient/use_cases/assign_therapist_use_case.py"
touch "$SRC_DIR/application/patient/schemas/__init__.py"
touch "$SRC_DIR/application/patient/schemas/patient_schemas.py"

# 3. Daily Log Context (核心域)
mkdir -p "$SRC_DIR/application/daily_log/use_cases"
mkdir -p "$SRC_DIR/application/daily_log/schemas"
touch "$SRC_DIR/application/daily_log/__init__.py"
touch "$SRC_DIR/application/daily_log/use_cases/__init__.py"
touch "$SRC_DIR/application/daily_log/use_cases/submit_daily_log_use_case.py"
touch "$SRC_DIR/application/daily_log/use_cases/get_daily_logs_use_case.py"
touch "$SRC_DIR/application/daily_log/use_cases/calculate_adherence_use_case.py"
touch "$SRC_DIR/application/daily_log/schemas/__init__.py"
touch "$SRC_DIR/application/daily_log/schemas/daily_log_schemas.py"

# 4. Survey Context (支撐子域)
mkdir -p "$SRC_DIR/application/survey/use_cases"
mkdir -p "$SRC_DIR/application/survey/schemas"
touch "$SRC_DIR/application/survey/__init__.py"
touch "$SRC_DIR/application/survey/use_cases/__init__.py"
touch "$SRC_DIR/application/survey/use_cases/submit_cat_survey_use_case.py"
touch "$SRC_DIR/application/survey/use_cases/submit_mmrc_survey_use_case.py"
touch "$SRC_DIR/application/survey/schemas/__init__.py"
touch "$SRC_DIR/application/survey/schemas/survey_schemas.py"

# 5. Risk Context (核心域)
mkdir -p "$SRC_DIR/application/risk/use_cases"
mkdir -p "$SRC_DIR/application/risk/schemas"
touch "$SRC_DIR/application/risk/__init__.py"
touch "$SRC_DIR/application/risk/use_cases/__init__.py"
touch "$SRC_DIR/application/risk/use_cases/calculate_risk_use_case.py"
touch "$SRC_DIR/application/risk/use_cases/trigger_alert_use_case.py"
touch "$SRC_DIR/application/risk/use_cases/acknowledge_alert_use_case.py"
touch "$SRC_DIR/application/risk/schemas/__init__.py"
touch "$SRC_DIR/application/risk/schemas/risk_schemas.py"

# 6. RAG Context (支撐子域 - 衛教知識庫)
mkdir -p "$SRC_DIR/application/rag/use_cases"
mkdir -p "$SRC_DIR/application/rag/schemas"
touch "$SRC_DIR/application/rag/__init__.py"
touch "$SRC_DIR/application/rag/use_cases/__init__.py"
touch "$SRC_DIR/application/rag/use_cases/query_knowledge_use_case.py"
touch "$SRC_DIR/application/rag/use_cases/voice_query_use_case.py"
touch "$SRC_DIR/application/rag/schemas/__init__.py"
touch "$SRC_DIR/application/rag/schemas/rag_schemas.py"

# 7. Notification Context (通用子域)
mkdir -p "$SRC_DIR/application/notification/use_cases"
mkdir -p "$SRC_DIR/application/notification/schemas"
touch "$SRC_DIR/application/notification/__init__.py"
touch "$SRC_DIR/application/notification/use_cases/__init__.py"
touch "$SRC_DIR/application/notification/use_cases/send_notification_use_case.py"
touch "$SRC_DIR/application/notification/use_cases/schedule_reminder_use_case.py"
touch "$SRC_DIR/application/notification/schemas/__init__.py"
touch "$SRC_DIR/application/notification/schemas/notification_schemas.py"

# ============================================
# Domain Layer - Entities, Value Objects, Services
# ============================================
echo "💎 創建 Domain Layer (Entities, Value Objects, Domain Services)..."

# Domain Entities (Aggregates)
mkdir -p "$SRC_DIR/domain/entities"
touch "$SRC_DIR/domain/entities/__init__.py"
touch "$SRC_DIR/domain/entities/user.py"
touch "$SRC_DIR/domain/entities/patient.py"
touch "$SRC_DIR/domain/entities/daily_log.py"
touch "$SRC_DIR/domain/entities/survey_response.py"
touch "$SRC_DIR/domain/entities/risk_score.py"
touch "$SRC_DIR/domain/entities/alert.py"
touch "$SRC_DIR/domain/entities/educational_document.py"
touch "$SRC_DIR/domain/entities/notification.py"

# Domain Value Objects
mkdir -p "$SRC_DIR/domain/value_objects"
touch "$SRC_DIR/domain/value_objects/__init__.py"
touch "$SRC_DIR/domain/value_objects/bmi.py"
touch "$SRC_DIR/domain/value_objects/medical_history.py"
touch "$SRC_DIR/domain/value_objects/smoking_history.py"
touch "$SRC_DIR/domain/value_objects/data_warning.py"
touch "$SRC_DIR/domain/value_objects/contributing_factors.py"
touch "$SRC_DIR/domain/value_objects/email.py"
touch "$SRC_DIR/domain/value_objects/hashed_password.py"

# Domain Services
mkdir -p "$SRC_DIR/domain/services"
touch "$SRC_DIR/domain/services/__init__.py"
touch "$SRC_DIR/domain/services/risk_engine.py"
touch "$SRC_DIR/domain/services/kpi_calculator.py"
touch "$SRC_DIR/domain/services/cat_scorer.py"
touch "$SRC_DIR/domain/services/mmrc_scorer.py"
touch "$SRC_DIR/domain/services/embedding_service.py"

# Domain Events
mkdir -p "$SRC_DIR/domain/events"
touch "$SRC_DIR/domain/events/__init__.py"
touch "$SRC_DIR/domain/events/auth_events.py"
touch "$SRC_DIR/domain/events/patient_events.py"
touch "$SRC_DIR/domain/events/daily_log_events.py"
touch "$SRC_DIR/domain/events/survey_events.py"
touch "$SRC_DIR/domain/events/risk_events.py"
touch "$SRC_DIR/domain/events/rag_events.py"
touch "$SRC_DIR/domain/events/notification_events.py"

# Domain Exceptions
mkdir -p "$SRC_DIR/domain/exceptions"
touch "$SRC_DIR/domain/exceptions/__init__.py"
touch "$SRC_DIR/domain/exceptions/domain_exceptions.py"

# Repository Interfaces (Ports)
mkdir -p "$SRC_DIR/domain/repositories"
touch "$SRC_DIR/domain/repositories/__init__.py"
touch "$SRC_DIR/domain/repositories/user_repository.py"
touch "$SRC_DIR/domain/repositories/patient_repository.py"
touch "$SRC_DIR/domain/repositories/daily_log_repository.py"
touch "$SRC_DIR/domain/repositories/survey_repository.py"
touch "$SRC_DIR/domain/repositories/risk_score_repository.py"
touch "$SRC_DIR/domain/repositories/alert_repository.py"
touch "$SRC_DIR/domain/repositories/document_repository.py"
touch "$SRC_DIR/domain/repositories/notification_repository.py"

# ============================================
# Infrastructure Layer - Adapters
# ============================================
echo "🔌 創建 Infrastructure Layer (Adapters)..."

# Database - SQLAlchemy ORM Models
mkdir -p "$SRC_DIR/infrastructure/database/models"
touch "$SRC_DIR/infrastructure/database/models/__init__.py"
touch "$SRC_DIR/infrastructure/database/models/user.py"
touch "$SRC_DIR/infrastructure/database/models/patient_profile.py"
touch "$SRC_DIR/infrastructure/database/models/therapist_profile.py"
touch "$SRC_DIR/infrastructure/database/models/daily_log.py"
touch "$SRC_DIR/infrastructure/database/models/survey_response.py"
touch "$SRC_DIR/infrastructure/database/models/risk_score.py"
touch "$SRC_DIR/infrastructure/database/models/alert.py"
touch "$SRC_DIR/infrastructure/database/models/educational_document.py"
touch "$SRC_DIR/infrastructure/database/models/document_chunk.py"
touch "$SRC_DIR/infrastructure/database/models/notification.py"
touch "$SRC_DIR/infrastructure/database/models/event_log.py"
touch "$SRC_DIR/infrastructure/database/models/ai_processing_log.py"
touch "$SRC_DIR/infrastructure/database/base.py"
touch "$SRC_DIR/infrastructure/database/session.py"

# Repositories Implementation (Adapters)
mkdir -p "$SRC_DIR/infrastructure/repositories"
touch "$SRC_DIR/infrastructure/repositories/__init__.py"
touch "$SRC_DIR/infrastructure/repositories/user_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/patient_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/daily_log_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/survey_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/risk_score_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/alert_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/document_repository_impl.py"
touch "$SRC_DIR/infrastructure/repositories/notification_repository_impl.py"

# External APIs Adapters
mkdir -p "$SRC_DIR/infrastructure/external_apis/openai"
mkdir -p "$SRC_DIR/infrastructure/external_apis/line"
touch "$SRC_DIR/infrastructure/external_apis/__init__.py"
touch "$SRC_DIR/infrastructure/external_apis/openai/__init__.py"
touch "$SRC_DIR/infrastructure/external_apis/openai/openai_client.py"
touch "$SRC_DIR/infrastructure/external_apis/openai/embedding_client.py"
touch "$SRC_DIR/infrastructure/external_apis/line/__init__.py"
touch "$SRC_DIR/infrastructure/external_apis/line/line_messaging_client.py"
touch "$SRC_DIR/infrastructure/external_apis/line/line_oauth_client.py"

# Message Queue (Event Bus) - Phase 2
mkdir -p "$SRC_DIR/infrastructure/message_queue/publishers"
mkdir -p "$SRC_DIR/infrastructure/message_queue/consumers"
mkdir -p "$SRC_DIR/infrastructure/message_queue/handlers"
touch "$SRC_DIR/infrastructure/message_queue/__init__.py"
touch "$SRC_DIR/infrastructure/message_queue/rabbitmq_client.py"
touch "$SRC_DIR/infrastructure/message_queue/in_memory_event_bus.py"
touch "$SRC_DIR/infrastructure/message_queue/publishers/__init__.py"
touch "$SRC_DIR/infrastructure/message_queue/publishers/event_publisher.py"
touch "$SRC_DIR/infrastructure/message_queue/consumers/__init__.py"
touch "$SRC_DIR/infrastructure/message_queue/consumers/daily_log_consumer.py"
touch "$SRC_DIR/infrastructure/message_queue/consumers/survey_consumer.py"
touch "$SRC_DIR/infrastructure/message_queue/handlers/__init__.py"
touch "$SRC_DIR/infrastructure/message_queue/handlers/risk_calculation_handler.py"
touch "$SRC_DIR/infrastructure/message_queue/handlers/notification_handler.py"

# Cache (Redis)
mkdir -p "$SRC_DIR/infrastructure/cache"
touch "$SRC_DIR/infrastructure/cache/__init__.py"
touch "$SRC_DIR/infrastructure/cache/redis_client.py"
touch "$SRC_DIR/infrastructure/cache/cache_keys.py"
touch "$SRC_DIR/infrastructure/cache/session_store.py"

# ============================================
# Core Layer - Shared Utilities
# ============================================
echo "⚙️  創建 Core Layer (Shared Cross-Cutting Concerns)..."
mkdir -p "$SRC_DIR/core/exceptions"
mkdir -p "$SRC_DIR/core/utils"
touch "$SRC_DIR/core/__init__.py"
touch "$SRC_DIR/core/config.py"
touch "$SRC_DIR/core/security.py"
touch "$SRC_DIR/core/dependencies.py"
touch "$SRC_DIR/core/exceptions/__init__.py"
touch "$SRC_DIR/core/exceptions/http_exceptions.py"
touch "$SRC_DIR/core/exceptions/application_exceptions.py"
touch "$SRC_DIR/core/utils/__init__.py"
touch "$SRC_DIR/core/utils/logger.py"
touch "$SRC_DIR/core/utils/datetime_utils.py"
touch "$SRC_DIR/core/utils/validators.py"

# ============================================
# Tests Structure (mirror src structure)
# ============================================
echo "🧪 創建測試目錄結構..."

# Unit Tests - Domain Layer
mkdir -p "$BACKEND_DIR/tests/unit/domain/entities"
mkdir -p "$BACKEND_DIR/tests/unit/domain/value_objects"
mkdir -p "$BACKEND_DIR/tests/unit/domain/services"
touch "$BACKEND_DIR/tests/__init__.py"
touch "$BACKEND_DIR/tests/conftest.py"
touch "$BACKEND_DIR/tests/unit/__init__.py"
touch "$BACKEND_DIR/tests/unit/domain/__init__.py"
touch "$BACKEND_DIR/tests/unit/domain/entities/__init__.py"
touch "$BACKEND_DIR/tests/unit/domain/entities/test_patient.py"
touch "$BACKEND_DIR/tests/unit/domain/entities/test_daily_log.py"
touch "$BACKEND_DIR/tests/unit/domain/entities/test_risk_score.py"
touch "$BACKEND_DIR/tests/unit/domain/value_objects/__init__.py"
touch "$BACKEND_DIR/tests/unit/domain/value_objects/test_bmi.py"
touch "$BACKEND_DIR/tests/unit/domain/value_objects/test_medical_history.py"
touch "$BACKEND_DIR/tests/unit/domain/services/__init__.py"
touch "$BACKEND_DIR/tests/unit/domain/services/test_risk_engine.py"
touch "$BACKEND_DIR/tests/unit/domain/services/test_kpi_calculator.py"

# Unit Tests - Application Layer
mkdir -p "$BACKEND_DIR/tests/unit/application/auth"
mkdir -p "$BACKEND_DIR/tests/unit/application/patient"
mkdir -p "$BACKEND_DIR/tests/unit/application/daily_log"
mkdir -p "$BACKEND_DIR/tests/unit/application/survey"
mkdir -p "$BACKEND_DIR/tests/unit/application/risk"
mkdir -p "$BACKEND_DIR/tests/unit/application/rag"
mkdir -p "$BACKEND_DIR/tests/unit/application/notification"
touch "$BACKEND_DIR/tests/unit/application/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/auth/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/auth/test_login_use_case.py"
touch "$BACKEND_DIR/tests/unit/application/patient/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/daily_log/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/daily_log/test_submit_daily_log_use_case.py"
touch "$BACKEND_DIR/tests/unit/application/survey/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/risk/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/rag/__init__.py"
touch "$BACKEND_DIR/tests/unit/application/notification/__init__.py"

# Integration Tests
mkdir -p "$BACKEND_DIR/tests/integration/api"
mkdir -p "$BACKEND_DIR/tests/integration/database"
mkdir -p "$BACKEND_DIR/tests/integration/external_apis"
touch "$BACKEND_DIR/tests/integration/__init__.py"
touch "$BACKEND_DIR/tests/integration/api/__init__.py"
touch "$BACKEND_DIR/tests/integration/api/test_auth_api.py"
touch "$BACKEND_DIR/tests/integration/api/test_daily_log_api.py"
touch "$BACKEND_DIR/tests/integration/database/__init__.py"
touch "$BACKEND_DIR/tests/integration/database/test_patient_repository.py"
touch "$BACKEND_DIR/tests/integration/external_apis/__init__.py"

# E2E Tests
mkdir -p "$BACKEND_DIR/tests/e2e"
touch "$BACKEND_DIR/tests/e2e/__init__.py"
touch "$BACKEND_DIR/tests/e2e/test_patient_journey.py"

# Test Fixtures
mkdir -p "$BACKEND_DIR/tests/fixtures"
touch "$BACKEND_DIR/tests/fixtures/__init__.py"
touch "$BACKEND_DIR/tests/fixtures/patient_fixtures.py"
touch "$BACKEND_DIR/tests/fixtures/daily_log_fixtures.py"

echo ""
echo "✅ Clean Architecture 目錄結構設置完成！"
echo ""
echo "📂 目錄結構概覽:"
echo "  ├── api/v1/routers/     (Presentation Layer - 7 個 API Router)"
echo "  ├── application/        (Application Layer - 7 個 Bounded Context)"
echo "  │   ├── auth/           (Auth Context - 通用子域)"
echo "  │   ├── patient/        (Patient Context - 支撐子域)"
echo "  │   ├── daily_log/      (Daily Log Context - 核心域 🔴)"
echo "  │   ├── survey/         (Survey Context - 支撐子域)"
echo "  │   ├── risk/           (Risk Context - 核心域 🔴)"
echo "  │   ├── rag/            (RAG Context - 支撐子域)"
echo "  │   └── notification/   (Notification Context - 通用子域)"
echo "  ├── domain/             (Domain Layer - 純業務邏輯)"
echo "  │   ├── entities/       (8 個 Aggregates)"
echo "  │   ├── value_objects/  (7 個 Value Objects)"
echo "  │   ├── services/       (5 個 Domain Services)"
echo "  │   ├── events/         (7 個 Event 模組)"
echo "  │   └── repositories/   (8 個 Repository Interfaces)"
echo "  ├── infrastructure/     (Infrastructure Layer - Adapters)"
echo "  │   ├── database/       (ORM Models + Session)"
echo "  │   ├── repositories/   (8 個 Repository Implementations)"
echo "  │   ├── external_apis/  (OpenAI, LINE Clients)"
echo "  │   ├── message_queue/  (Event Bus - Phase 2)"
echo "  │   └── cache/          (Redis Client)"
echo "  ├── core/               (Shared Utilities)"
echo "  └── tests/              (Unit + Integration + E2E)"
echo ""
echo "🎯 符合以下設計文檔:"
echo "  - 05_architecture_and_design.md (§4.1.1 模組劃分)"
echo "  - 10_class_relationships_and_module_design.md (UML 類別設計)"
echo "  - 08_project_structure_guide.md (目錄規範)"
