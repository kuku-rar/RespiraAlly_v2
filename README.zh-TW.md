# RespiraAlly V2.0 - COPD 患者健康照護平台

[English](README.md)

> **一個由 AI 驅動的健康照護平台，專為 COPD 患者管理設計，整合了 LINE、語音互動與智慧風險評估功能**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)

## 📋 目錄

- [專案總覽](#專案總覽)
  - [專案狀態](#專案狀態)
- [主要功能](#主要功能)
- [系統架構](#系統架構)
- [技術棧](#技術棧)
- [快速入門](#快速入門)
- [專案結構](#專案結構)
- [開發流程](#開發流程)
- [專案文件](#專案文件)
- [貢獻](#貢獻)
- [授權](#授權)

## 🎯 專案總覽

RespiraAlly V2.0 是一個創新的數位健康管理平台，旨在支援慢性阻塞性肺病 (COPD) 患者及其醫療照護提供者。平台結合了智慧提醒、AI 語音互動、即時風險評估以及全面的患者儀表板，將被動治療轉化為主動預防。

### 商業目標

- **賦能患者**：透過 LINE 提供易於使用且個人化的健康管理工具
- **提升醫療效率**：使治療師能夠有效地管理多位患者
- **預防性照護**：透過 AI 驅動的分析及早識別健康風險
- **促進行為改變**：達到 ≥75% 的健康行為遵從率

### 成功指標

- **北極星指標**：健康行為遵從率 ≥ 75%
- 患者 30 天留存率 (D30)
- 治療師每週登入頻率
- AI 回應準確率 ≥ 85%

### 📊 專案狀態

**當前階段**：Sprint 0 - 專案設定與架構設計 (進行中)

| 指標 | 狀態 |
|--------|--------|
| **整體進度** | 7.2% (71h / 983h) |
| **當前 Sprint** | Sprint 0 - 35.7% 已完成 |
| **專案開始日期** | 2025-10-18 |
| **預計 MVP 發布** | 2026-Q1 |
| **總時程** | 16 週 (8 個 Sprint × 14 天) |

**已完成的里程碑** ✅：

- ✅ **專案管理設定** (19.5% - 17h/87h)
  - WBS 開發計畫 v2.2
  - 8 個 Sprint 時程規劃
  - Git 工作流程 SOP & PR 審查 SLA
  - CI/CD 品質閘門設定
  - Conventional Commits 強制規範 (commitlint + husky)

- ✅ **系統架構設計** (48% - 54h/112h)
  - C4 架構圖 (Level 1-2)
  - 資料庫結構設計 (PostgreSQL 搭配 pgvector)
  - RESTful API 規格書
  - 前端架構規格書 (儀表板 + LIFF)
  - 長者優先設計原則文件
  - ADR (架構決策紀錄) × 8

**當前 Sprint 0 焦點**：
- ⏳ DDD 戰略設計與模組邊界定稿
- ⏳ 準備開發環境設定
- 📅 下一步：Sprint 1 (基礎設施與身份驗證) 將於第 1 週開始

**品質閘門狀態**：
- ✅ Commitlint 掛鉤已啟用
- ✅ CI/CD 管線已設定 (Black, Ruff, Mypy, Pytest, Prettier, ESLint)
- ✅ PR 審查 SLA 政策 (<24 小時首次審查)

詳細進度追蹤請見 [WBS 開發計畫](docs/16_wbs_development_plan.md)

## ✨ 主要功能

### 為患者設計 (LINE Bot + LIFF)

- 🔐 **簡易註冊**：透過 LINE User ID 快速註冊
- 📝 **每日健康日誌**：簡易表單追蹤症狀、用藥和活動
- 🎙️ **AI 語音問答**：使用語音（支援台語/國語）詢問健康問題
- 📊 **健康趨勢**：查看 7 天和 30 天的健康進度圖表
- 📋 **問卷評估**：完成 CAT/mMRC 評估量表
- ⚠️ **智慧警示**：接收個人化的健康提醒

### 為治療師設計 (網頁儀表板)

- 👥 **患者管理**：帶有風險指標的綜合患者列表
- 📈 **360° 患者檔案**：完整的健康歷史和分析數據
- 🚨 **風險評估中心**：高風險患者的即時警示
- 📅 **任務管理**：指派和追蹤患者後續任務
- 📊 **分析儀表板**：群體健康趨勢與洞察

### AI 功能

- 🧠 **RAG 系統**：結合醫學知識庫的檢索增強生成技術
- 🎤 **語音轉文字**：基於 Whisper 的 STT 語音輸入
- 💬 **LLM 處理**：由 GPT-4 驅動的智慧回應
- 🔊 **文字轉語音**：用於回應的自然語音合成
- 📖 **來源引用**：提供參考資料的透明 AI 推理過程

## 🏗️ 系統架構

### 系統架構圖

```
┌─────────────────────────────────────────────────────────┐
│                     LINE 平台                           │
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
│  患者服務 │      │  認證服務 │      │ 儀表板 (Next.js) │
└───────────┘      └───────────┘      └───────────────┘
    │                     │
    │              ┌──────▼──────┐
    │              │  風險引擎   │
    │              └─────────────┘
    │
┌───▼────────────────────────────────────┐
│        AI Worker (非同步)              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌────┐ │
│  │ STT  ├──► LLM  ├──► TTS  ├──►WS  │ │
│  └──────┘  └──────┘  └──────┘  └────┘ │
└────────────────────────────────────────┘
```

### 技術分層

1. **表現層 (Presentation Layer)**：LINE Bot, LIFF, Next.js 儀表板
2. **應用層 (Application Layer)**：FastAPI 使用案例與業務工作流程
3. **領域層 (Domain Layer)**：核心業務邏輯 (乾淨架構)
4. **基礎設施層 (Infrastructure Layer)**：PostgreSQL, Redis, RabbitMQ, MongoDB

## 🛠️ 技術棧

### 後端

- **框架**: FastAPI 0.109+
- **語言**: Python 3.11+
- **ORM**: SQLAlchemy 2.0+
- **資料庫**: PostgreSQL 15+ with pgvector
- **快取**: Redis 7+
- **訊息佇列**: RabbitMQ 3+
- **事件儲存**: MongoDB 7+

### 前端

- **儀表板**: Next.js 14+ (App Router), React 18+, TypeScript, Tailwind CSS
- **LIFF**: Vite, React 18+, TypeScript, Tailwind CSS
- **狀態管理**: Zustand, TanStack Query

### AI/機器學習

- **STT**: OpenAI Whisper API
- **LLM**: OpenAI GPT-4 Turbo
- **TTS**: Emotion-TTS / OpenAI TTS
- **RAG**: LangChain + pgvector + BM25 混合檢索
- **Embeddings**: OpenAI text-embedding-3-small

### 開發維運 (DevOps)

- **容器化**: Docker, Docker Compose
- **部署**: Zeabur
- **CI/CD**: GitHub Actions
- **監控**: Prometheus, Grafana, Sentry

## 🚀 快速入門

### 先決條件

- **Python**: 3.11+
- **Node.js**: 18.17+
- **uv**: 最新版本
- **Docker**: 最新版本
- **Docker Compose**: 最新版本

### 快速開始

1. **複製儲存庫**

```bash
git clone <repository-url>
cd RespiraAlly
```

2. **設定環境變數**

```bash
cp .env.example .env
# 編輯 .env 檔案並填入您的設定
```

3. **啟動基礎設施服務**

```bash
# 啟動 PostgreSQL, Redis, RabbitMQ, MongoDB
docker-compose up -d
```

4. **設定後端**

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn respira_ally.main:app --reload
```

5. **設定前端 (儀表板)**

```bash
cd frontend/dashboard
npm install
npm run dev
```

6. **設定前端 (LIFF)**

```bash
cd frontend/liff
npm install
npm run dev
```

### 服務入口

- **後端 API**: http://localhost:8000
- **API 文件**: http://localhost:8000/docs
- **儀表板**: http://localhost:3000
- **LIFF**: http://localhost:5173
- **RabbitMQ 管理介面**: http://localhost:15672 (guest/guest)

## 📁 專案結構

```
RespiraAlly/
├── backend/                    # FastAPI 後端服務
│   ├── src/respira_ally/
│   │   ├── api/                # API 端點 (表現層)
│   │   ├── application/        # 使用案例 (應用層)
│   │   ├── core/               # 核心工具與設定
│   │   ├── domain/             # 領域模型 (領域層)
│   │   └── infrastructure/     # 外部整合 (基礎設施層)
│   ├── tests/                  # 測試套件
│   └── pyproject.toml          # Python 依賴性管理
│
├── frontend/
│   ├── dashboard/              # 治療師儀表板 (Next.js)
│   │   ├── app/                # Next.js App Router
│   │   ├── components/         # React 元件
│   │   └── lib/                # 工具函式與 API 客戶端
│   │
│   └── liff/                   # 患者 LIFF 應用 (Vite + React)
│       ├── src/
│       │   ├── pages/          # 頁面元件
│       │   ├── components/     # 可重用元件
│       │   └── services/       # API 服務
│       └── vite.config.ts
│
├── docs/                       # 專案文件
│   ├── adr/                    # 架構決策紀錄
│   ├── bdd/                    # BDD 情境
│   ├── 02_product_requirements_document.md
│   ├── 05_architecture_and_design.md
│   ├── 06_api_design_specification.md
│   └── 16_wbs_development_plan.md
│
├── scripts/                    # 開發與部署腳本
├── .github/workflows/          # CI/CD 工作流程
├── docker-compose.yml          # 本地開發環境
└── README.md                   # 本檔案
```

## 💻 開發流程

### 分支策略

- `main`: 準備部署到生產環境的程式碼
- `develop`: 開發整合分支
- `feature/*`: 功能開發分支
- `fix/*`: 錯誤修復分支
- `hotfix/*`: 生產環境緊急修復分支

### 提交慣例

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

```
feat(api): 新增患者註冊端點
fix(liff): 解決語音錄製問題
docs(readme): 更新安裝說明
refactor(domain): 簡化風險計算邏輯
test(auth): 新增 JWT 權杖驗證測試
```

### 程式碼品質

```bash
# 後端
cd backend
uv run black src tests           # 格式化
uv run ruff check src tests      # 程式碼檢查
uv run mypy src                  # 型別檢查
uv run pytest                    # 測試

# 前端儀表板
cd frontend/dashboard
npm run lint                         # 程式碼檢查
npm run type-check                   # 型別檢查
npm test                             # 測試

# 前端 LIFF
cd frontend/liff
npm run lint                         # 程式碼檢查
npm run type-check                   # 型別檢查
```

### 測試策略

- **單元測試**: 領域邏輯、工具函式 (覆蓋率 ≥80%)
- **整合測試**: API 端點、資料庫操作
- **E2E 測試**: 關鍵使用者流程
- **效能測試**: API 回應時間、AI 處理延遲

## 📚 專案文件

### 核心文件

- **[產品需求文件](docs/02_product_requirements_document.md)** - 業務需求與使用者故事
- **[架構與設計](docs/05_architecture_and_design.md)** - 系統架構 (C4 模型, DDD)
- **[API 規格書](docs/06_api_design_specification.md)** - REST API 合約
- **[模組規格書](docs/07_module_specification_and_tests.md)** - 詳細模組設計
- **[WBS 開發計畫](docs/16_wbs_development_plan.md)** - 專案時程與任務

### 專案管理文件

- **[開發工作流程](docs/01_development_workflow.md)** - 開發流程與品質閘門
- **[Git 工作流程 SOP](docs/project_management/git_workflow_sop.md)** - 分支策略與提交慣例
- **[PR 審查 SLA 政策](docs/project_management/pr_review_sla_policy.md)** - 程式碼審查服務等級協議
- **[Git Hooks 設定指南](docs/project_management/setup_git_hooks.md)** - Commitlint 與 husky 設定

### 架構決策紀錄 (ADR)

- [ADR-001: FastAPI vs Flask](docs/adr/ADR-001-fastapi-vs-flask.md)
- [ADR-002: pgvector for Vector DB](docs/adr/ADR-002-pgvector-for-vector-db.md)
- [ADR-003: MongoDB for Event Logs](docs/adr/ADR-003-mongodb-for-event-logs.md)
- [ADR-004: LINE as Patient Entrypoint](docs/adr/ADR-004-line-as-patient-entrypoint.md)
- [ADR-005: RabbitMQ for Message Queue](docs/adr/ADR-005-rabbitmq-for-message-queue.md)

### BDD 情境

- [Epic 100: 身份驗證](docs/bdd/epic_100_authentication.feature)
- [Epic 200: 每日管理](docs/bdd/epic_200_daily_management.feature)
- [Epic 300: AI 互動](docs/bdd/epic_300_ai_interaction.feature)

## 🗓️ 專案時程

**總時程**: 16 週 (8 個 Sprint × 14 天) | **開始日期**: 2025-10-18 | **MVP 發布**: 2026 Q1

| Sprint | 焦點 | 時長 | 狀態 |
|--------|-------|----------|--------|
| **Sprint 0** | 規劃與架構 | 第 0 週 | 🔄 進行中 (35.7%) |
| **Sprint 1-2** | 基礎設施與身份驗證 | 第 1-4 週 | ⏳ 已規劃 |
| **Sprint 3-4** | 核心功能 (患者管理, 日誌, 風險) | 第 5-8 週 | ⏳ 已規劃 |
| **Sprint 5-6** | AI 功能 (RAG, 語音鏈) | 第 9-12 週 | ⏳ 已規劃 |
| **Sprint 7-8** | 優化與部署 | 第 13-16 週 | ⏳ 已規劃 |

**當前狀態**: Sprint 0 (規劃與架構) - 35.7% 已完成
- 詳細分解請見 [WBS 開發計畫](docs/16_wbs_development_plan.md)

## 🤝 貢獻

此為 AIPE01 期末專題學術專案，貢獻僅限於專案團隊成員。

### 團隊角色

- **專案經理**: Sprint 規劃、進度追蹤
- **技術負責人**: 後端架構、程式碼審查
- **產品負責人**: 需求定義、驗收標準
- **系統架構師**: C4 架構、DDD 策略、ADR 撰寫
- **AI/ML 工程師**: RAG 系統、STT/LLM/TTS 整合
- **前端工程師**: React/Next.js, LIFF, 儀表板 UI/UX
- **品保工程師**: 測試策略、自動化、品質保證
- **DevOps 工程師**: CI/CD, 部署, 監控

## 📄 授權

MIT 授權 - 詳情請見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- **LINE Platform**: 提供訊息傳遞與 LIFF 框架
- **OpenAI**: 提供 AI/ML 功能
- **FastAPI**: 提供現代化的 Python 網頁框架
- **Next.js**: 提供 React 框架
- **VibeCoding**: 提供企業級工作流程模板

---

**由 RespiraAlly 團隊用心打造 | AIPE01 Final Project 2025-2026**
