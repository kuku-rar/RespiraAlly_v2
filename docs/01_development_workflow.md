# RespiraAlly 開發工作流程手冊 (Development Workflow Cookbook)

---

**文件版本 (Document Version):** `v2.0`
**最後更新 (Last Updated):** `2025-10-18`
**主要作者 (Lead Author):** `Gemini Code AI`
**狀態 (Status):** `活躍 (Active)`

---

## Ⅰ. 核心目標

本文件為 `RespiraAlly` 專案的開發人員提供一套標準化、可執行的工作流程。其目標是確保程式碼品質、統一開發實踐，並提升團隊協作效率。這是一份「實踐手冊」，包含具體的指令與步驟。

## Ⅱ. 環境設定 (Initial Setup)

在開始之前，請確保您的本機環境已安裝 `git`, `node` (v18+), `npm` (v9+), `python` (v3.11+), 和 `uv`。

1.  **Clone 專案庫:**
    ```bash
    git clone https://github.com/your-repo/RespiraAlly.git
    cd RespiraAlly
    ```

2.  **安裝後端 (Backend) 依賴:**
    *   進入後端目錄並使用 uv 安裝。
    ```bash
    cd backend
    uv sync
    ```

3.  **安裝前端 (Frontend) 依賴:**
    *   本專案有兩個前端應用，請分別安裝。

    *   **治療師儀表板 (Dashboard):**
        ```bash
        cd frontend/dashboard
        npm install
        ```

    *   **病患 LIFF 應用:**
        ```bash
        cd frontend/liff
        npm install
        ```

## Ⅲ. 開發週期 (Development Cycle)

### 1. 建立分支 (Branching)

所有開發工作都應在獨立的分支上進行。請從 `main` 分支建立新分支。

**分支命名慣例:**

*   **新功能:** `feature/<ticket-id>-short-description` (e.g., `feature/RA-123-patient-list-view`)
*   **錯誤修復:** `fix/<ticket-id>-short-description` (e.g., `fix/RA-124-login-button-bug`)
*   **技術任務/重構:** `chore/<ticket-id>-short-description` (e.g., `chore/RA-125-refactor-api-service`)
*   **文件:** `docs/<ticket-id>-short-description` (e.g., `docs/RA-126-update-workflow-guide`)

### 2. 編寫程式碼 (Coding)

*   **後端 (Backend):**
    *   在 `backend` 目錄下執行開發伺服器：
    ```bash
    cd backend
    uv run uvicorn respira_ally.main:app --reload
    ```

*   **前端儀表板 (Frontend Dashboard):**
    *   在 `frontend/dashboard` 目錄下執行開發伺服器：
    ```bash
    cd frontend/dashboard
    npm run dev
    ```

*   **前端 LIFF (Frontend LIFF):**
    *   在 `frontend/liff` 目錄下執行開發伺服器：
    ```bash
    cd frontend/liff
    npm run dev
    ```

### 3. 品質保證 (Quality Assurance)

在提交程式碼前，必須在本機執行所有品質檢查。

*   **後端 (Backend):**
    *   在 `backend` 目錄下執行：
    ```bash
    # 格式化
    uv run black .
    # Linting
    uv run ruff check . --fix
    # 型別檢查
    uv run mypy .
    # 單元測試
    uv run pytest
    ```

*   **前端 (Frontend - Dashboard & LIFF):**
    *   在對應的 `frontend/dashboard` 或 `frontend/liff` 目錄下執行：
    ```bash
    # 格式化
    npm run format
    # Linting
    npm run lint
    # 型別檢查
    npm run type-check
    # 測試 (僅限 Dashboard)
    npm test
    ```

### 4. 提交變更 (Committing)

我們遵循 **Conventional Commits** 規範。這有助於自動化版本管理和變更日誌的生成。

**Commit 訊息格式:**

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

*   **`<type>` 類型:** `feat`, `fix`, `build`, `chore`, `ci`, `docs`, `perf`, `refactor`, `revert`, `style`, `test`
*   **範例:**
    ```
    feat(api): add endpoint for patient data retrieval

    Implements the GET /api/v1/patients/{id} endpoint to fetch detailed
    information for a specific patient.

    Resolves: RA-123
    ```

### 5. 拉取請求 (Pull Request)

1.  **Push 分支:**
    ```bash
    git push origin feature/RA-123-patient-list-view
    ```

2.  **建立 Pull Request (PR):**
    *   在 GitHub 上，從您的分支建立一個指向 `main` 分支的 Pull Request。
    *   **標題:** 應清晰描述 PR 的目的，通常是您的主要 Commit 訊息。
    *   **描述:** 使用 PR 範本，連結到相關的 Jira Ticket (e.g., `RA-123`)，並簡要說明變更內容、原因以及任何需要注意的測試細節。

3.  **程式碼審查 (Code Review):**
    *   您的 PR 必須至少獲得一位其他團隊成員的批准 (Approve)。
    *   所有 GitHub Actions CI/CD 檢查（包括測試、Linting、建置）必須全部通過。

4.  **合併 (Merging):**
    *   在獲得批准且所有檢查通過後，使用 **Squash and Merge** 將您的變更合併到 `main` 分支。這能保持 `main` 分支的提交歷史乾淨、線性。

## Ⅳ. CI/CD

本專案使用 GitHub Actions 進行持續整合與部署。當您建立 PR 或將變更推送到 `main` 分支時，系統會自動觸發以下流程：

*   **後端:** 執行 Linting, 型別檢查, 單元測試, 並建置 Docker 映像。
*   **前端:** 執行 Linting, 型別檢查, 測試 (如適用), 並建置靜態資源。

請確保您的所有變更都能順利通過這些自動化檢查。