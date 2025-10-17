# RespiraAlly 專案結構指南

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-16`
**主要作者:** `Claude Code AI`
**狀態:** `活躍 (Active)`

---

## 1. 指南目的

*   為 `RespiraAlly V2.0` 提供一個標準化、可擴展且易於理解的目錄和文件結構。
*   確保團隊成員能夠快速定位代碼、配置文件和文檔。
*   促進代碼的模塊化和關注點分離，與我們的 Clean Architecture 設計原則保持一致。

## 2. 核心設計原則

*   **按功能組織 (Organize by Feature)**: 相關的功能（例如，用戶認證、日誌管理）應盡可能放在一起，而不是按技術類型（e.g., `routers`, `models`）分散在各處。
*   **明確的職責**: 每個頂層目錄都有其單一、明確的職責。
*   **一致的命名**: 文件和目錄的命名遵循一致的、可預測的約定。
*   **配置外部化**: 應用程式的配置應與代碼分離，便於在不同環境中部署。
*   **根目錄簡潔**: 根目錄只包含專案級別的配置文件，原始碼應放在專用的 `src/` 目錄下。

## 3. 頂層目錄結構 (Monorepo)

本專案採用 Monorepo 結構，將後端、前端和共享資源放在同一個 Git 倉庫中，便於統一管理。

```plaintext
respira-ally/
├── .github/              # CI/CD 工作流程 (GitHub Actions)
├── .vscode/              # VS Code 編輯器特定配置
├── backend/              # 所有後端服務 (Python/FastAPI)
├── frontend/             # 所有前端應用
│   ├── dashboard/        # 治療師儀表板 (Next.js)
│   └── liff/             # 病患 LIFF 應用 (React/Vite)
├── docs/                 # 專案文檔 (本文檔、ADRs、設計文檔等)
├── scripts/              # 開發和運維腳本
├── .gitignore
├── docker-compose.yml    # 本地開發環境定義
└── README.md             # 專案介紹和快速入門指南
```

## 4. 目錄詳解

### 4.1 `backend/` - 後端原始碼

後端遵循 Clean Architecture 分層，並按業務領域劃分模組。

```plaintext
backend/
├── alembic/              # 資料庫遷移腳本
├── src/
│   └── respira_ally/
│       ├── __init__.py
│       ├── main.py         # FastAPI 應用程式入口點
│       │
│       ├── api/            # Presentation Layer: API Routers
│       │   ├── __init__.py
│       │   ├── deps.py     # 依賴注入
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── auth.py
│       │       ├── daily_logs.py
│       │       └── patients.py
│       │
│       ├── application/    # Application Layer: Use Cases
│       │   ├── __init__.py
│       │   ├── auth/
│       │   ├── daily_logs/
│       │   └── patients/
│       │       ├── __init__.py
│       │       ├── schemas.py    # Pydantic DTOs
│       │       └── services.py   # Use Case 實現
│       │
│       ├── core/           # 跨功能共享的核心邏輯
│       │   ├── __init__.py
│       │   ├── config.py   # 配置加載
│       │   └── security.py # 認證、授權
│       │
│       ├── domain/         # Domain Layer: 核心業務領域模型
│       │   ├── __init__.py
│       │   ├── models/     # 業務實體 (Entities)
│       │   └── repositories/ # Repository 接口定義 (Ports)
│       │
│       └── infrastructure/ # Infrastructure Layer
│           ├── __init__.py
│           ├── database/
│           │   ├── __init__.py
│           │   ├── models/       # SQLAlchemy ORM Models
│           │   └── session.py    # 資料庫會話管理
│           └── repositories/     # Repository 實現 (Adapters)
│               ├── __init__.py
│               └── patient_repository.py
│
├── tests/                # 測試代碼 (結構與 src/ 對應)
├── pyproject.toml        # Python 專案定義、依賴 (Poetry)
└── poetry.lock
```

### 4.2 `frontend/` - 前端原始碼

前端分為兩個獨立的應用：`dashboard` 和 `liff`。

#### `frontend/dashboard/` (Next.js)
```plaintext
frontend/dashboard/
├── components/           # 可重用 UI 元件
├── app/                  # Next.js App Router
│   ├── (auth)/login/     # 登入頁 (路由群組)
│   └── (main)/           # 主佈局
│       ├── layout.tsx
│       ├── page.tsx      # 主儀表板頁面
│       └── patients/
│           └── [id]/
│               └── page.tsx # 病患詳情頁
├── lib/                  # 輔助函式, API 客戶端
├── styles/               # 全域樣式
├── package.json
└── next.config.js
```

#### `frontend/liff/` (Vite + React)
```plaintext
frontend/liff/
├── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/            # 自定義 Hooks
│   ├── pages/            # 頁面元件
│   │   ├── DailyLog.tsx
│   │   └── Register.tsx
│   ├── services/         # API 呼叫邏輯
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### 4.3 `docs/` - 文檔
所有與專案相關的長篇文檔都存放在此，包括本文檔。
```plaintext
docs/
├── adr/                  # 架構決策記錄
├── bdd/                  # BDD 情境
├── images/               # 文檔中使用的圖片
├── api_design_specification.md
├── architecture_and_design.md
└── ...
```

## 5. 文件命名約定

*   **Python 模組:** `snake_case.py`
*   **測試文件:** `test_*.py`
*   **React 元件:** `PascalCase.tsx`
*   **Markdown 文件 & 目錄:** `kebab-case` 或 `snake_case`
