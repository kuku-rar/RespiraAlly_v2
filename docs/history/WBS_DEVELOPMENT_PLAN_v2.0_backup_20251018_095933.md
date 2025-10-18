# RespiraAlly V2.0 工作分解結構 (WBS) 開發計劃

---

**文件版本 (Document Version):** `v2.0`
**最後更新 (Last Updated):** `2025-10-18`
**主要作者 (Lead Author):** `TaskMaster Hub / Claude Code AI`
**審核者 (Reviewers):** `Technical Lead, Product Manager, Architecture Team`
**狀態 (Status):** `執行中 - Sprint 0 架構設計進行中 (In Progress - Sprint 0 Architecture Design In Progress)`

---

## 目錄 (Table of Contents)

1. [專案總覽 (Project Overview)](#1-專案總覽-project-overview)
2. [WBS 結構總覽 (WBS Structure Overview)](#2-wbs-結構總覽-wbs-structure-overview)
3. [詳細任務分解 (Detailed Task Breakdown)](#3-詳細任務分解-detailed-task-breakdown)
4. [專案進度摘要 (Project Progress Summary)](#4-專案進度摘要-project-progress-summary)
5. [風險與議題管理 (Risk & Issue Management)](#5-風險與議題管理-risk--issue-management)
6. [品質指標與里程碑 (Quality Metrics & Milestones)](#6-品質指標與里程碑-quality-metrics--milestones)

---

## 1. 專案總覽 (Project Overview)

### 🎯 專案基本資訊

| 項目 | 內容 |
|------|------|
| **專案名稱** | RespiraAlly V2.0 - COPD Patient Healthcare Platform |
| **專案經理** | TaskMaster Hub (AI-Powered Project Coordination) |
| **技術主導** | Backend Lead, Frontend Lead, AI/ML Specialist |
| **專案狀態** | 執行中 (In Progress) - 目前進度: ~5.9% 完成 (Sprint 0 架構設計進行中) |
| **文件版本** | v2.0 |
| **最後更新** | 2025-10-18 |

### ⏱️ 專案時程規劃

| 項目 | 日期/時間 |
|------|----------|
| **總工期** | 16 週 (8 Sprints × 14 days) (2025-10-21 ～ 2026-02-12) |
| **目前進度** | ~5.9% 完成 (~54h/912h，Sprint 0 架構設計進行中) |
| **當前階段** | Sprint 0 準備 - 架構設計、數據庫設計、前端架構完成 |
| **預計交付** | 2026-Q1 (V2.0 MVP Release) |

### 👥 專案角色與職責

| 角色 | 負責人 | 主要職責 |
|------|--------|----------|
| **專案經理 (PM)** | TaskMaster Hub | Sprint 規劃、進度追蹤、風險管理、團隊協調 |
| **技術負責人 (TL)** | Backend Lead | FastAPI 架構、技術決策、代碼審查 |
| **產品經理 (PO)** | Product Owner | 需求定義、使用者故事、驗收標準、優先級排序 |
| **架構師 (ARCH)** | System Architect | C4 架構設計、DDD 戰略、技術選型、ADR 撰寫 |
| **AI/ML 工程師** | AI Specialist | RAG 系統、STT/LLM/TTS 整合、語音處理鏈 |
| **前端工程師** | Frontend Lead | Next.js Dashboard、LIFF、UI/UX |
| **質量控制 (QA)** | QA Engineer | 測試策略、自動化測試、品質保證 |
| **DevOps** | DevOps Engineer | CI/CD、Zeabur 部署、監控配置 |

---

## 2. WBS 結構總覽 (WBS Structure Overview)

### 📊 WBS 樹狀結構 (基於 8 Sprint 規劃)

```
1.0 專案管理與規劃 (Project Management) [16h]
├── 1.1 專案啟動與規劃 [8h]
├── 1.2 Sprint 規劃與執行 [6h]
└── 1.3 專案監控與報告 [2h]

2.0 系統架構與設計 (System Architecture) [112h] ✅ 48%
├── 2.1 技術架構設計 [32h] ✅ 25%
├── 2.2 資料庫設計 (PostgreSQL + pgvector) [24h] ✅ 67%
├── 2.3 API 設計規範 [16h] ✅ 38%
├── 2.4 前端架構設計 [32h] ✅ 100%
└── 2.5 DDD 戰略設計 [8h]

3.0 Sprint 1: 基礎設施 & 認證系統 [96h] [Week 1-2]
├── 3.1 環境建置與容器化 [20h]
├── 3.2 資料庫 Schema 實作 [16h]
├── 3.3 FastAPI 專案結構 [16h]
├── 3.4 認證授權系統 [32h]
└── 3.5 前端基礎架構 [20h]

4.0 Sprint 2: 病患管理 & 日誌功能 [112h] [Week 3-4]
├── 4.1 個案管理 API [28h]
├── 4.2 日誌服務 API [32h]
├── 4.3 LIFF 日誌表單 [28h]
└── 4.4 Dashboard 病患列表 [24h]

5.0 Sprint 3: 儀表板 & 問卷系統 [96h] [Week 5-6]
├── 5.1 個案 360° 頁面 [32h]
├── 5.2 CAT/mMRC 問卷 API [24h]
├── 5.3 LIFF 問卷頁 [24h]
└── 5.4 趨勢圖表元件 [16h]

6.0 Sprint 4: 風險引擎 & 預警 [104h] [Week 7-8]
├── 6.1 風險分數計算引擎 [32h]
├── 6.2 異常規則引擎 [28h]
├── 6.3 任務管理 API [24h]
└── 6.4 Dashboard 預警中心 [20h]

7.0 Sprint 5: RAG 系統基礎 [80h] [Week 9-10]
├── 7.1 pgvector 擴展與向量化 [24h]
├── 7.2 衛教內容管理 API [20h]
├── 7.3 Hybrid 檢索實作 [28h]
└── 7.4 Dashboard 衛教管理頁 [8h]

8.0 Sprint 6: AI 語音處理鏈 [88h] [Week 11-12]
├── 8.1 RabbitMQ 任務佇列 [16h]
├── 8.2 AI Worker 服務 [40h]
├── 8.3 LIFF 語音錄製介面 [20h]
└── 8.4 WebSocket 推送機制 [12h]

9.0 Sprint 7: 通知系統 & 排程 [72h] [Week 13-14]
├── 9.1 APScheduler 排程服務 [16h]
├── 9.2 通知服務與提醒規則 [32h]
├── 9.3 週報自動生成 [16h]
└── 9.4 Dashboard 通知歷史 [8h]

10.0 Sprint 8: 優化 & 上線準備 [96h] [Week 15-16]
├── 10.1 效能優化 [24h]
├── 10.2 監控與告警 [20h]
├── 10.3 安全稽核 [16h]
├── 10.4 部署與 CI/CD [20h]
└── 10.5 文檔與培訓 [16h]

11.0 測試與品質保證 (Continuous) [80h]
├── 11.1 單元測試 [32h]
├── 11.2 整合測試 [24h]
├── 11.3 端到端測試 [16h]
└── 11.4 效能測試 [8h]
```

### 📈 工作包統計概覽

| WBS 模組 | 總工時 | 已完成 | 進度 | 狀態圖示 |
|---------|--------|--------|------|----------|
| 1.0 專案管理 | 16h | 0h | 0% | ⬜ |
| 2.0 系統架構 | 112h | 54h | 48% | 🔄 |
| 3.0 Sprint 1 (基礎設施) | 96h | 0h | 0% | ⬜ |
| 4.0 Sprint 2 (病患管理) | 112h | 0h | 0% | ⬜ |
| 5.0 Sprint 3 (儀表板) | 96h | 0h | 0% | ⬜ |
| 6.0 Sprint 4 (風險引擎) | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 (RAG 系統) | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 (AI 語音) | 88h | 0h | 0% | ⬜ |
| 9.0 Sprint 7 (通知系統) | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 (優化上線) | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 (持續) | 80h | 0h | 0% | ⬜ |
| **總計** | **912h** | **54h** | **~5.9%** | **🔄** |

**狀態圖示說明:**
- ✅ 已完成 (Completed)
- 🔄 進行中 (In Progress)
- ⚡ 接近完成 (Near Completion)
- ⏳ 計劃中 (Planned)
- ⬜ 未開始 (Not Started)

**⚠️ 重要架構決策變更記錄:**
- **v2.0 更新 (2025-10-18)**:
  - ✅ 移除所有 MongoDB 相關任務 - 改用 PostgreSQL JSONB 替代
  - ✅ 微服務架構 → Modular Monolith (MVP Phase 0-2)
  - ✅ 新增前端架構設計階段 (2.4)
  - ✅ 重新計算工時統計 (936h → 912h)

---

## 3. 詳細任務分解 (Detailed Task Breakdown)

### 1.0 專案管理與規劃 (Project Management)

#### 1.1 專案啟動與規劃
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 1.1.1 | 專案章程制定 | PM | 2 | ⬜ | TBD | - | - |
| 1.1.2 | WBS 結構設計 | PM | 3 | ⬜ | TBD | 1.1.1 | - |
| 1.1.3 | 8 Sprint 時程規劃 | PM | 2 | ⬜ | TBD | 1.1.2 | - |
| 1.1.4 | 風險識別與評估 | TL | 1 | ⬜ | TBD | 1.1.3 | - |

#### 1.2 Sprint 規劃與執行
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 1.2.1 | Sprint Planning 儀式 | PM | 2 | ⬜ | 每 Sprint | - | - |
| 1.2.2 | Daily Standup 執行 | Team | 2 | ⬜ | 每日 | - | - |
| 1.2.3 | Sprint Review & Retro | PM | 2 | ⬜ | 每 Sprint 末 | - | - |

#### 1.3 專案監控與報告
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 1.3.1 | 週報告制度建立 | PM | 1 | ⬜ | Sprint 1 | - | - |
| 1.3.2 | TaskMaster 進度追蹤 | PM | 1 | ⬜ | 持續 | 1.3.1 | - |

**1.0 專案管理小計**: 16h | 進度: 0% (0/16h 已完成)

---

### 2.0 系統架構與設計 (System Architecture)

#### 2.1 技術架構設計
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.1.1 | C4 Level 1-2 架構圖 | ARCH | 8 | ✅ | 2025-10-17 | 1.1.2 | 05_architecture_and_design.md |
| 2.1.2 | Modular Monolith 模組邊界劃分 | ARCH | 8 | ⬜ | Sprint 0 | 2.1.1 | ADR-001 |
| 2.1.3 | Clean Architecture 分層設計 | ARCH | 8 | ⬜ | Sprint 0 | 2.1.2 | - |
| 2.1.4 | 事件驅動架構設計 | ARCH | 8 | ⬜ | Sprint 0 | 2.1.3 | - |

**關鍵變更**: MVP 採用 **Modular Monolith** 而非微服務，Phase 3 後可拆分。

#### 2.2 資料庫設計 (PostgreSQL Only)
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.2.1 | PostgreSQL ER 圖設計 | Data Engineer | 8 | ✅ | 2025-10-17 | 2.1.2 | database/schema_design_v1.0.md |
| 2.2.2 | 完整表結構設計 (13 tables) | Data Engineer | 8 | ✅ | 2025-10-17 | 2.2.1 | database/schema_design_v1.0.md |
| 2.2.3 | pgvector 向量表設計 | Data Engineer | 4 | ⬜ | Sprint 4 | 2.2.2 | ADR-002 |
| 2.2.4 | 索引策略規劃 | Data Engineer | 4 | ⬜ | Sprint 0 | 2.2.2 | - |

**⚠️ 重大變更**: 移除 MongoDB，使用 **PostgreSQL JSONB** 替代 (event_logs 表)。

#### 2.3 API 設計規範
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.3.1 | RESTful API 規範制定 | TL | 6 | ✅ | 2025-10-17 | 2.1.2 | 06_api_design_specification.md |
| 2.3.2 | OpenAPI Schema 定義 | TL | 6 | ⬜ | Sprint 1 | 2.3.1 | - |
| 2.3.3 | 錯誤處理標準 | TL | 2 | ⬜ | Sprint 1 | 2.3.2 | - |
| 2.3.4 | JWT 認證授權設計 | Security | 4 | ⬜ | Sprint 0 | 2.3.3 | - |

#### 2.4 前端架構設計 ✅ 已完成
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.4.1 | 前端技術棧規範制定 | Frontend Lead | 8 | ✅ | 2025-10-18 | 2.1.2 | 12_frontend_architecture_specification.md |
| 2.4.2 | 前端信息架構設計 | Frontend Lead, UX | 16 | ✅ | 2025-10-18 | 2.4.1 | 17_frontend_information_architecture_template.md |
| 2.4.3 | Elder-First 設計原則文檔 | UX Designer | 4 | ✅ | 2025-10-18 | 2.4.1 | 包含在 12_frontend_architecture_specification.md |
| 2.4.4 | 前後端 API 契約對齊驗證 | Frontend Lead, TL | 4 | ✅ | 2025-10-18 | 2.4.2, 2.3.1 | - |

**技術決策**:
- Next.js 14 (App Router) + TanStack Query + Zustand
- LINE LIFF (病患端) + Next.js Dashboard (治療師端)
- Elder-First 設計: 18px 字體, 44px 觸控目標

#### 2.5 DDD 戰略設計
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.5.1 | 界限上下文映射 | ARCH | 4 | ⬜ | Sprint 0 | 2.1.2 | - |
| 2.5.2 | 統一語言 (Ubiquitous Language) 定義 | ARCH, PO | 2 | ⬜ | Sprint 0 | 2.5.1 | - |
| 2.5.3 | 聚合根識別與設計 | ARCH | 2 | ⬜ | Sprint 1 | 2.5.2 | - |

**2.0 系統架構小計**: 112h | 進度: 48% (54/112h 已完成)

---

### 3.0 Sprint 1: 基礎設施 & 認證系統 [Week 1-2]

**Sprint 目標**: 建立可運行的專案骨架,完成 Docker 環境、資料庫、FastAPI 結構與使用者認證。

#### 3.1 環境建置與容器化
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.1.1 | Docker Compose 定義 | DevOps | 4 | ⬜ | Week 1 | - | - |
| 3.1.2 | PostgreSQL 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | - |
| 3.1.3 | Redis 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | - |
| 3.1.4 | RabbitMQ 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | ADR-005 |
| 3.1.5 | MinIO 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | - |
| 3.1.6 | 開發環境驗證 | DevOps | 2 | ⬜ | Week 1 | 3.1.5 | - |
| 3.1.7 | `.env` 環境變數管理 | DevOps | 2 | ⬜ | Week 1 | 3.1.6 | - |
| 3.1.8 | GitHub Actions CI/CD 初始化 | DevOps | 4 | ⬜ | Week 2 | 3.1.7 | - |

#### 3.2 資料庫 Schema 實作
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.2.1 | Alembic 初始化 | Backend | 2 | ⬜ | Week 1 | 2.2.4 | - |
| 3.2.2 | 核心表 Migration (users, profiles) | Backend | 4 | ⬜ | Week 1 | 3.2.1 | - |
| 3.2.3 | 業務表 Migration (daily_logs, surveys) | Backend | 4 | ⬜ | Week 1 | 3.2.2 | - |
| 3.2.4 | 事件表 Migration (event_logs JSONB) | Backend | 2 | ⬜ | Week 1 | 3.2.3 | - |
| 3.2.5 | SQLAlchemy Models 定義 | Backend | 4 | ⬜ | Week 1 | 3.2.4 | - |

**關鍵變更**: 使用 PostgreSQL `event_logs` 表 (JSONB) 替代 MongoDB。

#### 3.3 FastAPI 專案結構
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.3.1 | Poetry 專案初始化 | Backend | 2 | ⬜ | Week 1 | - | ADR-001 |
| 3.3.2 | Clean Architecture 目錄結構 | Backend | 3 | ⬜ | Week 1 | 3.3.1, 2.1.3 | - |
| 3.3.3 | FastAPI `main.py` 入口點 | Backend | 2 | ⬜ | Week 1 | 3.3.2 | - |
| 3.3.4 | Database Session 管理 | Backend | 3 | ⬜ | Week 1 | 3.3.3, 3.2.5 | - |
| 3.3.5 | Pydantic Settings 配置加載 | Backend | 2 | ⬜ | Week 1 | 3.3.4 | - |
| 3.3.6 | 全域錯誤處理 Middleware | Backend | 2 | ⬜ | Week 2 | 3.3.5, 2.3.3 | - |
| 3.3.7 | CORS Middleware 配置 | Backend | 1 | ⬜ | Week 2 | 3.3.6 | - |
| 3.3.8 | `/health` Endpoint 實作 | Backend | 1 | ⬜ | Week 2 | 3.3.7 | - |

#### 3.4 認證授權系統
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.4.1 | JWT Token 生成邏輯 | Backend | 4 | ⬜ | Week 1 | 2.3.4 | - |
| 3.4.2 | JWT Token 驗證 Dependency | Backend | 4 | ⬜ | Week 1 | 3.4.1 | - |
| 3.4.3 | RBAC 權限檢查 Decorator | Backend | 4 | ⬜ | Week 2 | 3.4.2 | - |
| 3.4.4 | LINE LIFF OAuth 整合 | Backend | 8 | ⬜ | Week 2 | 3.4.3 | ADR-004 |
| 3.4.5 | `POST /auth/register` API (US-101) | Backend | 4 | ⬜ | Week 2 | 3.4.4 | - |
| 3.4.6 | `POST /auth/token` API (US-102) | Backend | 4 | ⬜ | Week 2 | 3.4.3 | - |
| 3.4.7 | 登入失敗鎖定策略 (Redis) | Backend | 4 | ⬜ | Week 2 | 3.4.6 | ADR-008 |

#### 3.5 前端基礎架構
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.5.1 | Next.js Dashboard 專案初始化 | Frontend | 4 | ⬜ | Week 1 | - | - |
| 3.5.2 | Vite + React LIFF 專案初始化 | Frontend | 4 | ⬜ | Week 1 | - | ADR-004 |
| 3.5.3 | Tailwind CSS 配置 | Frontend | 2 | ⬜ | Week 1 | 3.5.1, 3.5.2 | - |
| 3.5.4 | API Client (Axios) 封裝 | Frontend | 4 | ⬜ | Week 2 | 3.5.3, 2.3.1 | - |
| 3.5.5 | Dashboard 登入頁 UI (US-102) | Frontend | 4 | ⬜ | Week 2 | 3.5.4, 3.4.6 | - |
| 3.5.6 | LIFF 註冊頁 UI (US-101) | Frontend | 2 | ⬜ | Week 2 | 3.5.4, 3.4.5 | - |

**3.0 Sprint 1 小計**: 96h | 進度: 0% (0/96h 已完成)
**關鍵交付物**: Docker Compose 環境, Database Schema, JWT 認證, 登入/註冊頁面

---

### 4.0 Sprint 2: 病患管理 & 日誌功能 [Week 3-4]

**Sprint 目標**: 完成病患 CRUD、日誌提交與查詢流程,治療師可查看病患列表。

#### 4.1 個案管理 API
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.1.1 | Patient Repository 實作 | Backend | 4 | ⬜ | Week 3 | 3.2.5 | - |
| 4.1.2 | Patient Application Service | Backend | 4 | ⬜ | Week 3 | 4.1.1 | - |
| 4.1.3 | `GET /patients` API (US-501) | Backend | 6 | ⬜ | Week 3 | 4.1.2 | - |
| 4.1.4 | `GET /patients/{id}` API 基礎版 | Backend | 4 | ⬜ | Week 3 | 4.1.3 | - |
| 4.1.5 | 查詢參數篩選邏輯 | Backend | 4 | ⬜ | Week 4 | 4.1.3 | - |
| 4.1.6 | 分頁與排序實作 | Backend | 4 | ⬜ | Week 4 | 4.1.5 | - |
| 4.1.7 | `POST /patients/{id}/assign` (US-103) | Backend | 2 | ⬜ | Week 4 | 4.1.4 | - |

#### 4.2 日誌服務 API
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.2.1 | DailyLog Domain Model | Backend | 4 | ⬜ | Week 3 | 2.5.3 | - |
| 4.2.2 | DailyLog Repository 實作 | Backend | 4 | ⬜ | Week 3 | 4.2.1 | - |
| 4.2.3 | DailyLog Application Service | Backend | 4 | ⬜ | Week 3 | 4.2.2 | - |
| 4.2.4 | `POST /daily-logs` API (US-201) | Backend | 6 | ⬜ | Week 3 | 4.2.3 | - |
| 4.2.5 | 每日唯一性檢查與更新邏輯 | Backend | 4 | ⬜ | Week 4 | 4.2.4 | - |
| 4.2.6 | `GET /daily-logs` 查詢 API | Backend | 4 | ⬜ | Week 4 | 4.2.5 | - |
| 4.2.7 | `daily_log.submitted` 事件發布 | Backend | 4 | ⬜ | Week 4 | 4.2.4, 2.1.4 | - |
| 4.2.8 | Idempotency Key 支援 | Backend | 2 | ⬜ | Week 4 | 4.2.5 | - |

#### 4.3 LIFF 日誌表單
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.3.1 | LIFF 日誌頁面路由 | Frontend | 2 | ⬜ | Week 3 | 3.5.2 | - |
| 4.3.2 | 日誌表單 UI 元件 | Frontend | 8 | ⬜ | Week 3 | 4.3.1 | - |
| 4.3.3 | Toggle (用藥) + Number Input | Frontend | 4 | ⬜ | Week 3 | 4.3.2 | - |
| 4.3.4 | 表單驗證邏輯 | Frontend | 4 | ⬜ | Week 4 | 4.3.3 | - |
| 4.3.5 | 提交後鼓勵訊息 | Frontend | 2 | ⬜ | Week 4 | 4.3.4, 4.2.4 | - |
| 4.3.6 | 錯誤處理與 Toast 提示 | Frontend | 4 | ⬜ | Week 4 | 4.3.5 | - |
| 4.3.7 | LIFF SDK 整合測試 | Frontend | 4 | ⬜ | Week 4 | 4.3.6 | - |

#### 4.4 Dashboard 病患列表
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.4.1 | Dashboard Layout 設計 | Frontend | 4 | ⬜ | Week 3 | 3.5.1 | - |
| 4.4.2 | 病患列表頁面 UI | Frontend | 6 | ⬜ | Week 3 | 4.4.1, 4.1.3 | - |
| 4.4.3 | Table 元件 (分頁、排序) | Frontend | 6 | ⬜ | Week 4 | 4.4.2 | - |
| 4.4.4 | 篩選器元件 (風險等級、依從率) | Frontend | 4 | ⬜ | Week 4 | 4.4.3 | - |
| 4.4.5 | 搜尋功能 | Frontend | 2 | ⬜ | Week 4 | 4.4.4 | - |
| 4.4.6 | 即時數據更新 (Polling/WebSocket) | Frontend | 2 | ⬜ | Week 4 | 4.4.5 | - |

**4.0 Sprint 2 小計**: 112h | 進度: 0% (0/112h 已完成)
**關鍵交付物**: 病患列表、日誌提交 API、LIFF 日誌表單

---

### 5.0 - 11.0 (後續 Sprints)

*為節省篇幅，Sprint 3-8 與測試品保章節保持原有結構，僅移除 MongoDB 相關任務。*

**5.0 Sprint 3: 儀表板 & 問卷系統 [96h]**
**6.0 Sprint 4: 風險引擎 & 預警 [104h]**
**7.0 Sprint 5: RAG 系統基礎 [80h]** (使用 pgvector)
**8.0 Sprint 6: AI 語音處理鏈 [88h]**
**9.0 Sprint 7: 通知系統 & 排程 [72h]**
**10.0 Sprint 8: 優化 & 上線準備 [96h]**
**11.0 測試與品質保證 [80h]**

---

## 4. 專案進度摘要 (Project Progress Summary)

### 🎯 整體進度統計

| WBS 模組 | 總工時 | 已完成 | 進度 | 狀態 |
|---------|--------|--------|------|------|
| 1.0 專案管理 | 16h | 0h | 0% | ⬜ |
| 2.0 系統架構 | 112h | 54h | 48% | 🔄 |
| 3.0 Sprint 1 | 96h | 0h | 0% | ⬜ |
| 4.0 Sprint 2 | 112h | 0h | 0% | ⬜ |
| 5.0 Sprint 3 | 96h | 0h | 0% | ⬜ |
| 6.0 Sprint 4 | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 | 88h | 0h | 0% | ⬜ |
| 9.0 Sprint 7 | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 | 80h | 0h | 0% | ⬜ |
| **總計** | **912h** | **54h** | **~5.9%** | **🔄** |

### 📅 Sprint 進度分析

#### 🔄 Sprint 0 (專案準備階段) - [進行中 ~48%]
- **已完成進度**: 54h/112h (系統架構與設計)
- **關鍵里程碑**:
  - ✅ C4 架構圖完成 (05_architecture_and_design.md)
  - ✅ 資料庫 Schema 設計完成 (database/schema_design_v1.0.md)
  - ✅ API 規範文件完成 (06_api_design_specification.md)
  - ✅ 前端架構規範完成 (12_frontend_architecture_specification.md)
  - ✅ 前端信息架構完成 (17_frontend_information_architecture_template.md)
  - ⬜ Modular Monolith 模組邊界劃分
  - ⬜ DDD 戰略設計

#### ⏳ Sprint 1 (Week 1-2) - [未開始]
- **預期進度**: +96h (3.0 模組)
- **關鍵里程碑**:
  - Docker Compose 環境可運行
  - PostgreSQL/Redis/RabbitMQ 正常連接
  - JWT 認證流程完整
  - 登入/註冊頁面可用

#### ⏳ Sprint 2-8 (Week 3-16) - [未開始]
- **預期進度**: +664h (4.0-10.0 模組)
- **關鍵里程碑**: 參見各 Sprint 詳細說明

---

## 5. 風險與議題管理 (Risk & Issue Management)

### 🚨 風險管控矩陣

#### 🔴 高風險項目
| 風險項目 | 影響度 | 可能性 | 緩解措施 | 負責人 | 參考 ADR |
|---------|--------|--------|----------|--------|---------|
| LINE API 配額不足導致推播失敗 | 高 | 中 | 優先使用 Reply API,監控 Push 用量,建立配額告警 | Backend Lead | ADR-004 |
| AI 模型回覆不當內容或延遲 | 高 | 中 | 信心分數閾值過濾,人工審核機制,備用 fallback 訊息 | AI/ML | - |
| pgvector 百萬級效能下降 | 中 | 高 | IVFFlat 索引優化,準備遷移至 Milvus 方案 | AI/ML | ADR-002 |
| Whisper 本地部署 GPU 需求高 | 中 | 高 | 優先使用 OpenAI Whisper API,Sprint 8 評估本地化 | AI/ML | - |
| RabbitMQ 單點故障風險 | 中 | 中 | Sprint 8 引入鏡像佇列,或遷移至 Kafka | DevOps | ADR-005 |
| 個資法合規風險 | 高 | 低 | 法規顧問審查,資料去識別化,審計日誌完整 | Security | - |

#### 🟡 中風險項目
| 風險項目 | 影響度 | 可能性 | 緩解措施 | 負責人 | 參考 ADR |
|---------|--------|--------|----------|--------|---------|
| 高齡使用者 LIFF 操作困難 | 中 | 高 | UAT 驗證,介面極簡化,語音互動為主 | Frontend | ADR-004 |
| Modular Monolith 模組耦合 | 中 | 中 | 嚴格模組邊界,Event Sourcing 解耦,定期重構 | Backend Lead | ADR-001 |
| CI/CD Pipeline 不穩定 | 中 | 中 | GitHub Actions 備用 Runner,測試環境隔離 | DevOps | - |

#### 🟢 低風險項目
| 風險項目 | 影響度 | 可能性 | 緩解措施 | 負責人 | 參考 ADR |
|---------|--------|--------|----------|--------|---------|
| Zeabur 平台穩定性 | 低 | 低 | 多區域部署,備份 K8s 部署方案 | DevOps | - |
| LINE Platform 服務中斷 | 低 | 低 | 監控 LINE 狀態頁,降級訊息通知 | Backend Lead | ADR-004 |

### 📋 議題追蹤清單

| 議題ID | 議題描述 | 嚴重程度 | 狀態 | 負責人 | 目標解決日期 |
|--------|----------|----------|------|--------|--------------|
| ISS-001 | ai-worker STT/LLM/TTS 服務選型未最終確定 | 高 | 開放 | AI/ML | Sprint 1 |
| ISS-002 | LIFF 本地測試需 ngrok,開發流程待建立 | 中 | 開放 | Frontend | Sprint 1 |
| ISS-003 | 風險分數公式權重是否可由治療師調整 | 中 | 開放 | PO | Sprint 4 |

---

## 6. 品質指標與里程碑 (Quality Metrics & Milestones)

### 🎯 關鍵里程碑

| 里程碑 | 預定日期 | 狀態 | 驗收標準 |
|--------|----------|------|----------|
| M0: 架構設計完成 | 2025-10-21 (Sprint 0 End) | 🔄 | C4 架構圖、DB Schema、API 規範、前端架構完成 (48% 已完成) |
| M1: 基礎設施完成 | 2025-11-03 (Sprint 1 End) | ⬜ | Docker 環境運行,JWT 認證完成,登入/註冊可用 |
| M2: 核心功能完成 | 2025-12-01 (Sprint 4 End) | ⬜ | 病患列表、日誌提交、風險評分、預警中心可用 |
| M3: AI 能力上線 | 2025-12-29 (Sprint 6 End) | ⬜ | 語音提問完整流程可用,15 秒內回覆 |
| M4: MVP 正式發布 | 2026-02-12 (Sprint 8 End) | ⬜ | 所有功能上線,效能達標,通過安全稽核,生產部署完成 |

### 📈 品質指標監控

#### ⏳ 待達成指標 (目標值)
- **測試覆蓋率**: 目標 ≥80% (目前 0%)
- **API P95 響應時間**: 目標 < 500ms
- **AI 語音回覆時間**: 目標 < 15 秒 (端到端)
- **錯誤率**: 目標 < 0.1%
- **服務可用性**: 目標 ≥99.5%
- **北極星指標 (健康行為依從率)**: 目標 ≥75% (V1 基準 ~45%)

### 💡 改善建議

#### 立即行動項目
1. **完成 Modular Monolith 模組邊界劃分**: 避免模組耦合
2. **確立 AI 服務商**: 盡快決定 STT/LLM/TTS 使用 OpenAI API 或本地模型,撰寫 ADR
3. **建立 LIFF 開發環境**: 配置 ngrok 與 LINE Developers Console,撰寫開發指南

#### 中長期優化
1. **技術債管理**: 每 Sprint 保留 20% 時間重構,建立 Tech Debt Log
2. **監控體系完善**: Sprint 8 後持續優化 Grafana Dashboard,建立告警 Runbook
3. **架構演進規劃**: 評估 pgvector → Milvus, RabbitMQ → Kafka, Modular Monolith → Microservices 的遷移時機

---

## 7. 專案管控機制

### 📊 進度報告週期
- **Daily Standup**: 開發團隊內部同步 (15 分鐘)
- **Weekly Report**: 利害關係人更新 (每週五)
- **Sprint Review**: 演示交付物 (Sprint 最後一天)
- **Sprint Retrospective**: 流程改進 (Sprint Review 後)

### 🔄 變更管控流程
1. **變更請求提交** → 2. **影響評估** → 3. **變更委員會審核** → 4. **批准/拒絕** → 5. **執行與追蹤**

**⚠️ 重要備註 - ADR 變更追蹤機制:**
- 所有 WBS 內容的重大變更(任務範圍、技術選型、架構決策、時程調整)都必須建立對應的 [ADR](./adr/)
- 變更類型與 ADR 要求:
  - **技術架構變更** → 必須建立 ADR (如資料庫選型、框架切換、部署方式調整)
  - **任務範圍調整** → 建議建立 ADR (如功能需求變更、模組重構、整合方式調整)
  - **時程或資源調整** → 視影響程度決定是否建立 ADR
- ADR 編號規則: `ADR-XXX-[主題]` (例如: ADR-001-modular-monolith)
- 每次 WBS 更新時,須在相關任務「ADR 參考」欄位註明 ADR 編號
- 變更歷史追蹤: 所有 ADR 應在 `docs/adr/README.md` 建立索引

**v2.0 重大變更記錄 (2025-10-18)**:
- ✅ **ADR-001 變更**: 微服務架構 → Modular Monolith (MVP Phase 0-2)
- ✅ **ADR-003 廢棄**: MongoDB 事件日誌 → PostgreSQL JSONB (event_logs 表)
- ✅ 移除 16h MongoDB 相關任務 (2.2.2, 3.1.3, 3.2.7, 7.2.5)
- ✅ 新增 32h 前端架構設計任務 (2.4.1-2.4.4)
- ✅ 總工時: 936h → 912h

### ⚖️ 資源分配原則
- **關鍵路徑優先**: Sprint 1 → Sprint 4 → Sprint 6 為關鍵路徑,優先分配資源
- **風險緩解優先**: 高風險項目 (LINE API 配額、AI 模型穩定性) 獲得額外資源保障
- **技能匹配**: 根據團隊成員專長分配任務 (Backend/Frontend/AI-ML/DevOps)
- **並行開發**: Sprint 2-7 可並行開發前後端,最大化團隊產出

---

**專案管理總結**: RespiraAlly V2.0 是一個高複雜度的 AI/ML Healthcare 專案,採用 8 Sprint 敏捷開發模式,總工時 912 小時。關鍵成功因素包括:技術架構的前置設計 (Sprint 0)、關鍵路徑的資源保障、風險的主動管理、以及測試品質的持續保證。

**架構決策**: MVP 階段採用 **Modular Monolith + PostgreSQL** 簡化技術棧，確保快速交付。Phase 3 後可根據實際需求拆分為微服務與專用向量資料庫。

**專案經理**: TaskMaster Hub / Claude Code AI
**最後更新**: 2025-10-18 09:40
**下次檢討**: 2025-10-21 (Sprint 1 Planning)

---

## 📝 專案進度更新日誌 (Progress Update Log)

### 2025-10-18 09:40 - v2.0 架構決策變更與進度更新

**✅ 完成項目** (Sprint 0 - 系統架構與設計):

1. **系統架構設計** (完成 8h)
   - ✅ C4 Level 1-2 架構圖 (05_architecture_and_design.md)

2. **資料庫設計** (完成 16h)
   - ✅ PostgreSQL ER 圖設計 (database/schema_design_v1.0.md)
   - ✅ 完整表結構設計 (13 tables, 含 event_logs JSONB 表)

3. **API 設計規範** (完成 6h)
   - ✅ RESTful API 規範制定 (06_api_design_specification.md)

4. **前端架構設計** (完成 32h) ⭐ 新增
   - ✅ 前端技術棧規範制定 (12_frontend_architecture_specification.md)
   - ✅ 前端信息架構設計 (17_frontend_information_architecture_template.md)
   - ✅ Elder-First 設計原則文檔
   - ✅ 前後端 API 契約對齊驗證

**架構決策變更**:

1. **ADR-001 更新**: 微服務 → **Modular Monolith**
   - 理由: MVP 階段簡化架構，降低開發與維運複雜度
   - 影響: 移除微服務邊界劃分任務，改為模組邊界設計

2. **ADR-003 廢棄**: MongoDB → **PostgreSQL JSONB**
   - 理由: 單一數據源，簡化技術棧，PostgreSQL JSONB 足夠靈活
   - 影響: 移除 4 個 MongoDB 任務 (共 16h)
   - 替代方案: event_logs 表使用 JSONB 欄位

**統計數據**:
- 已完成工時: 54h / 912h = **5.9%**
- 系統架構模組: 54h / 112h = **48%**
- 下一步: 完成 DDD 戰略設計與模組邊界劃分

---

**相關文檔連結**:
- **核心決策文檔**: [ADR 架構決策記錄](./adr/)
- [產品需求文件 (PRD)](./02_product_requirements_document.md)
- [系統架構設計文檔](./05_architecture_and_design.md)
- [資料庫 Schema 設計](./database/schema_design_v1.0.md)
- [API 設計規格](./06_api_design_specification.md)
- [前端架構規範](./12_frontend_architecture_specification.md)
- [前端信息架構](./17_frontend_information_architecture_template.md)
- [模組規格與測試](./07_module_specification_and_tests.md)
- [專案結構指南](./08_project_structure_guide.md)

---

*此 WBS 遵循 VibeCoding 開發流程規範,整合 TaskMaster Hub 智能協調機制,確保專案品質與交付效率。*
