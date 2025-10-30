# Changelog

All notable changes to RespiraAlly V2.0 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🚀 Sprint 6 Phase 1: LLM + RAG Agent System (2025-10-29)

**狀態**: ✅ **80% 完成** - Agent 系統與知識庫就緒，pgvector 相容性待修復

#### ✨ Added
- **CrewAI Agent System**: Multi-agent AI 架構實作完成
  - ✅ Guardrail Agent (安全檢查代理) - memory=False 模式
  - ✅ Health Agent (健康照護代理) - 整合 RAG 知識檢索
  - ✅ AgentManager (協調器) - 兩階段處理流程
  - 技術棧: CrewAI 0.28.0 + LangChain ChatOpenAI

- **COPD 知識庫系統**: pgvector 語義搜尋基礎建設
  - ✅ **153 筆 COPD Q&A** 載入完成（含 OpenAI embeddings）
  - ✅ **96 個詳細分類**：疾病認識、藥物治療、呼吸訓練、營養飲食等
  - ✅ **OpenAI text-embedding-3-small** (1536 維向量)
  - ✅ **pgvector 擴充功能**已啟用
  - 資料來源: `backend/data/COPD_QA.xlsx`

- **AI Tools Implementation**:
  - ✅ GuardrailTool - 使用 OpenAI 判斷輸入安全性（違法/成人/不當醫療內容）
  - ✅ COPDKnowledgeTool - pgvector 語義搜尋（待修復相容性問題）

#### 🐛 Fixed
- **P1 Critical**: CrewAI 0.28.0 導入相容性問題修復
  - 問題: `cannot import name 'LLM' from 'crewai'`
  - 根本原因: CrewAI 0.28.0 不提供 LLM 和 BaseTool 類別，需使用 LangChain
  - 解決方案:
    - Agents: `from langchain_openai import ChatOpenAI` (取代 `from crewai import LLM`)
    - Tools: `from langchain.tools import BaseTool` (取代 `from crewai.tools import BaseTool`)
  - 影響檔案:
    - `backend/src/respira_ally/agents/guardrail_agent.py`
    - `backend/src/respira_ally/agents/health_agent.py`
    - `backend/src/respira_ally/tools/guardrail_tool.py`
    - `backend/src/respira_ally/tools/rag_tool.py`
  - 驗證: ✅ 所有模組導入測試通過

- **P0 Critical**: PostgreSQL enum schema mismatch for Task model (2025-10-28)
  - Root cause: Alembic migration created enum types without schema specification
  - Solution: Aligned database columns and SQLAlchemy model to use `development` schema enums
  - Files modified: `backend/src/respira_ally/infrastructure/database/models/task.py`
  - Impact: Task Board drag-and-drop now fully functional, status updates persist to database
  - Verification: ✅ E2E tested with Playwright, API returns 200 OK, database updates confirmed

#### ⚠️ Known Issues
- **pgvector + asyncpg 相容性問題** (ISSUE-001)
  - 症狀: `asyncpg.exceptions.UndefinedObjectError: type "vector" does not exist`
  - 根本原因: asyncpg 需要明確註冊自訂 PostgreSQL 類型（如 pgvector 的 `vector` 類型）
  - 影響: 向量語義搜尋功能暫時無法使用
  - 變通方案: 可使用關鍵字搜尋（`search_by_keywords` 方法）
  - 待修復: 需在連接池啟動時註冊 pgvector 類型
  - 優先級: P1 (不阻塞其他功能開發)

#### 🏗️ Architecture
- **DDD Repository Pattern**: 知識庫與對話歷史分離關注點
  - `domain/repositories/knowledge_repository.py` - 知識庫介面
  - `domain/repositories/conversation_repository.py` - 對話歷史介面
  - `infrastructure/repository_impls/pgvector_knowledge_repository.py` - pgvector 實作
  - `infrastructure/repository_impls/redis_conversation_repository.py` - Redis 實作

- **Agent 協作模式**: 遵循 beloved_grandson 設計原則
  - memory=False - 不使用 CrewAI 內建 ChromaDB 記憶
  - Repository Pattern - 使用 DDD 介面分離關注點
  - 兩階段處理 - Guardrail 檢查 → Health Agent 回覆
  - Fallback 機制 - CrewAI 失敗時降級為 OpenAI + RAG

#### 📊 Metrics
- **知識庫覆蓋度**: 153 筆 Q&A，涵蓋 96 個 COPD 照護主題
- **向量維度**: 1536 維 (OpenAI text-embedding-3-small)
- **預估 Token 使用**:
  - Guardrail 檢查: ~100-200 tokens
  - RAG 檢索: ~1000-1500 tokens（含檢索結果）
  - Health Agent 回覆: ~200-500 tokens
  - **單次對話**: ~1300-2200 tokens
- **預估成本** (gpt-4o-mini): ~$0.0003-0.0005 USD/對話

### 🚀 Sprint 6 Planning
- ✅ Agent System 基礎實作 (Guardrail + Health + RAG)
- ✅ COPD 知識庫載入 (153 筆 Q&A)
- 🔄 pgvector 語義搜尋修復 (asyncpg 相容性)
- ⏳ LINE Webhook → RabbitMQ Publisher
- ⏳ RabbitMQ Consumer + Agent 調用
- ⏳ 端到端測試 (LINE → Agent → Response)
- ⏳ Notification System MVP: Design and implementation
- ⏳ Alert Lifecycle Management: Acknowledge/Resolve endpoints
- ⏳ Technical Debt: Database-driven rule engine (DEBT-001)

---

## [Archived]

**Sprint 5 (2025-10-27)**: Task Management System + Alert UI
- 詳細內容已歸檔至：`docs/dev_logs/CHANGELOG_20251027.md`（繁體中文版本）

**Sprint 4 (2025-10-26)**: Alert System MVP + Exacerbation Management API
- 詳細內容已歸檔至：`docs/dev_logs/CHANGELOG_20251026.md`（繁體中文版本）

**Sprint 3 (2025-10-22)**: Risk Assessment API with GOLD ABE Classification
**Sprint 2 (2025-10-15)**: Authentication System, Database Setup
**Sprint 1 (2025-10-08)**: Project Initialization, Architecture Design

---

## Legend

- ✨ **Added**: New features
- 🔄 **Changed**: Changes in existing functionality
- 🗑️ **Deprecated**: Soon-to-be removed features
- ❌ **Removed**: Now removed features
- 🐛 **Fixed**: Bug fixes
- 🔒 **Security**: Vulnerability fixes
- 📚 **Documentation**: Documentation-only changes
- 🏗️ **Architecture**: Architectural decisions and design changes
- ✅ **Testing**: Testing-related changes
- 📊 **Metrics**: KPIs, performance metrics, analytics

---

**Maintained by**: TaskMaster Hub Coordination System
**Review Frequency**: End of each sprint
**Format**: Keep a Changelog v1.0.0
