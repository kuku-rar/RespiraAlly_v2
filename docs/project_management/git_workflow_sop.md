# Git Workflow 標準作業程序 (SOP)

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-18`
**負責人 (Owner):** `Technical Lead`
**狀態 (Status):** `已批准 (Approved)`

---

## 目錄 (Table of Contents)

1. [核心原則 (Core Principles)](#1-核心原則-core-principles)
2. [分支策略 (Branching Strategy)](#2-分支策略-branching-strategy)
3. [工作流程 (Workflow)](#3-工作流程-workflow)
4. [Merge 策略 (Merge Strategy)](#4-merge-策略-merge-strategy)
5. [衝突處理 (Conflict Resolution)](#5-衝突處理-conflict-resolution)
6. [緊急修復 (Hotfix)](#6-緊急修復-hotfix)
7. [常見問題 (FAQ)](#7-常見問題-faq)

---

## 1. 核心原則 (Core Principles)

### 🎯 **Linus Torvalds Git 哲學**

> "Git is not about branches. Git is about commits."
> Git 不是關於分支，而是關於提交。

**三大鐵律**:
1. ✅ **Never Break Main** - 永遠不破壞 main 分支
2. ✅ **Commit Early, Commit Often** - 頻繁提交，保持小單位
3. ✅ **Write Good Commit Messages** - 寫好的 Commit 訊息 (未來的你會感謝現在的你)

**禁止事項**:
- ❌ 直接在 main 分支上開發
- ❌ `git push --force` 到 main/master
- ❌ 未經 Code Review 的 Merge
- ❌ Commit 包含敏感資料 (.env, credentials.json)
- ❌ 使用 `git add .` 盲目加入所有文件 (先 `git status` 檢查)

---

## 2. 分支策略 (Branching Strategy)

### 📊 **分支架構**

```
main (受保護)
  ├── feature/RA-XXX-short-description  (新功能)
  ├── fix/RA-XXX-short-description      (錯誤修復)
  ├── chore/RA-XXX-short-description    (技術任務/重構)
  ├── docs/RA-XXX-short-description     (文件)
  └── hotfix/RA-XXX-critical-issue      (緊急修復)
```

### 🏷️ **分支命名規範**

**格式**: `<type>/<ticket-id>-<short-description>`

| 類型 | 用途 | 範例 | 生命週期 |
|------|------|------|----------|
| `feature/` | 新功能開發 | `feature/RA-123-patient-list-view` | 1-5 天 |
| `fix/` | Bug 修復 | `fix/RA-124-login-button-bug` | 1-2 天 |
| `chore/` | 技術任務、重構、依賴更新 | `chore/RA-125-refactor-api-service` | 1-3 天 |
| `docs/` | 文件更新 | `docs/RA-126-update-workflow-guide` | 幾小時 |
| `hotfix/` | 生產環境緊急修復 | `hotfix/RA-127-critical-data-leak` | 立即 |

**命名規則**:
- ✅ 全小寫
- ✅ 使用 `-` 分隔單字 (不用 `_` 或空格)
- ✅ 描述性但簡潔 (< 50 字元)
- ✅ 必須包含 Ticket ID (RA-XXX)

**範例**:
```bash
# ✅ 正確
git checkout -b feature/RA-201-daily-log-submission
git checkout -b fix/RA-202-auth-token-expiry
git checkout -b chore/RA-203-upgrade-fastapi-to-0.110

# ❌ 錯誤
git checkout -b new-feature              # 缺少 Ticket ID
git checkout -b Feature/RA-123-Test      # 大寫
git checkout -b feature/RA_123_test      # 使用底線
git checkout -b feature/add-patient-management-module-with-full-crud  # 太長
```

---

## 3. 工作流程 (Workflow)

### 📝 **標準開發流程** (5 個步驟)

#### **Step 1: 建立分支**

```bash
# 1. 確保 main 分支最新
git checkout main
git pull origin main

# 2. 建立新分支
git checkout -b feature/RA-123-patient-list-view

# 3. 驗證分支
git branch  # 應該看到 * feature/RA-123-patient-list-view
```

#### **Step 2: 開發與提交**

```bash
# 1. 進行開發工作
# ... (編輯程式碼) ...

# 2. 檢查變更
git status
git diff  # 檢查修改內容

# 3. 暫存變更 (分批暫存，不要一次全部)
git add backend/src/api/patients.py
git add backend/tests/test_patients.py

# 4. 提交 (使用 Conventional Commits)
git commit -m "feat(api): add GET /patients endpoint

Implements the patient list retrieval API with pagination
and filtering support.

- Add PatientRepository.list() method
- Add query params: limit, offset, status
- Add unit tests for patient listing

Resolves: RA-123"

# 5. 頻繁推送到遠端 (每日至少一次)
git push origin feature/RA-123-patient-list-view
```

**Conventional Commits 格式**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 類型**:
- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文件變更
- `style`: 格式調整 (不影響邏輯)
- `refactor`: 重構
- `perf`: 效能優化
- `test`: 測試
- `build`: 建置系統
- `ci`: CI 配置
- `chore`: 雜項

**範例**:
```bash
# ✅ 正確
git commit -m "feat(auth): add JWT token refresh mechanism"
git commit -m "fix(api): resolve null pointer in patient query"
git commit -m "docs(readme): update installation steps"

# ❌ 錯誤
git commit -m "update"           # 太簡略
git commit -m "Add feature"      # 不符合格式
git commit -m "WIP"              # 無意義
```

#### **Step 3: 保持同步**

```bash
# 定期同步 main 分支的最新變更 (每天至少一次)
git checkout main
git pull origin main
git checkout feature/RA-123-patient-list-view
git rebase main  # 或 git merge main (依團隊政策)

# 如果有衝突,解決後繼續
git add <resolved-files>
git rebase --continue
```

#### **Step 4: Code Review 前的檢查**

```bash
# 1. 執行所有品質檢查 (見 01_development_workflow.md §Ⅲ.3)
# 後端
cd backend
uv run black .
uv run ruff check . --fix
uv run mypy .
uv run pytest

# 前端
cd frontend/dashboard
npm run format
npm run lint
npm run type-check
npm test

# 2. 確保所有測試通過
# 3. 檢查是否有未提交的變更
git status

# 4. 推送最新版本
git push origin feature/RA-123-patient-list-view
```

#### **Step 5: 建立 Pull Request**

```bash
# 使用 GitHub CLI (推薦)
gh pr create --title "feat(api): add patient list endpoint" \
             --body "$(cat <<'EOF'
## Summary
Implements GET /patients API endpoint with pagination and filtering.

## Changes
- Add PatientRepository.list() method
- Add query params: limit, offset, status
- Add comprehensive unit tests

## Test Plan
- [x] Unit tests pass (pytest)
- [x] Manual testing with Postman
- [x] Edge cases: empty list, invalid params

## Resolves
RA-123

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
             --base main

# 或透過 GitHub Web UI
# 1. 前往 https://github.com/kuku-rar/RespiraAlly_v2/pulls
# 2. 點擊 "New pull request"
# 3. 選擇分支: base: main <- compare: feature/RA-123-patient-list-view
# 4. 填寫 PR 模板
```

---

## 4. Merge 策略 (Merge Strategy)

### 🔀 **Squash and Merge (預設策略)**

**理由**: 保持 main 分支的提交歷史乾淨、線性

```bash
# GitHub 上執行 Squash and Merge 後,本地清理分支
git checkout main
git pull origin main
git branch -d feature/RA-123-patient-list-view  # 刪除本地分支
git push origin --delete feature/RA-123-patient-list-view  # 刪除遠端分支 (可選)
```

**Squash Merge 流程**:
1. ✅ PR 獲得至少 1 個 Approve
2. ✅ 所有 CI 檢查通過 (GitHub Actions)
3. ✅ 無 Merge Conflict
4. ✅ 點擊 "Squash and merge"
5. ✅ 編輯 Commit 訊息 (預設為 PR 標題)
6. ✅ 確認 Merge

**結果**:
```
main: A -- B -- C -- [D: feat(api): add patient list endpoint]
                      ↑ (squashed from 5 commits in feature branch)
```

---

## 5. 衝突處理 (Conflict Resolution)

### ⚠️ **Merge Conflict 處理流程**

#### **情境: Rebase 時遇到衝突**

```bash
# 1. 嘗試 rebase
git checkout feature/RA-123-patient-list-view
git rebase main

# 輸出: CONFLICT (content): Merge conflict in backend/src/api/patients.py

# 2. 查看衝突檔案
git status
# Unmerged paths:
#   both modified:   backend/src/api/patients.py

# 3. 打開檔案編輯,移除衝突標記
# <<<<<<< HEAD (main 分支的版本)
# 你的程式碼
# =======
# main 分支的程式碼
# >>>>>>> feature/RA-123-patient-list-view

# 4. 解決衝突後,標記為已解決
git add backend/src/api/patients.py

# 5. 繼續 rebase
git rebase --continue

# 6. 如果太複雜,可以中止 rebase
git rebase --abort
```

#### **情境: PR 有衝突**

```bash
# GitHub 提示: "This branch has conflicts that must be resolved"

# 方法 1: 本地解決 (推薦)
git checkout feature/RA-123-patient-list-view
git pull origin main
# 解決衝突 (同上)
git add <resolved-files>
git commit -m "chore: resolve merge conflicts with main"
git push origin feature/RA-123-patient-list-view

# 方法 2: GitHub Web UI 解決 (簡單衝突)
# 點擊 "Resolve conflicts" 按鈕
```

### 🚨 **衝突預防**

1. ✅ **頻繁同步**: 每天至少一次 `git pull origin main`
2. ✅ **小分支**: 功能分支壽命 < 3 天
3. ✅ **溝通**: 多人編輯同一檔案前先協調

---

## 6. 緊急修復 (Hotfix)

### 🔥 **生產環境緊急修復流程**

**適用情境**: 生產環境發現嚴重 Bug,需要立即修復

```bash
# 1. 從 main 建立 hotfix 分支
git checkout main
git pull origin main
git checkout -b hotfix/RA-999-critical-auth-bypass

# 2. 快速修復 (最小化變更)
# ... (編輯程式碼) ...

# 3. 測試修復
uv run pytest tests/test_auth.py -v

# 4. 提交修復
git add backend/src/auth/jwt.py
git commit -m "fix(auth): patch critical JWT validation bypass

Security issue: JWT tokens were not validating expiry correctly,
allowing expired tokens to authenticate.

Fix: Add explicit exp claim validation in verify_token()

Impact: Critical - affects all authenticated endpoints
Severity: P0
Resolves: RA-999"

# 5. 推送並建立 PR (標記為緊急)
git push origin hotfix/RA-999-critical-auth-bypass
gh pr create --title "🔥 HOTFIX: critical auth bypass" \
             --label "priority:critical" \
             --assignee @technical-lead

# 6. 快速 Review + Merge (可能需要管理員權限繞過檢查)
# 7. 部署到生產環境
# 8. 通知團隊

# 9. Merge 後清理
git checkout main
git pull origin main
git branch -d hotfix/RA-999-critical-auth-bypass
```

**Hotfix 優先級**:
- **P0 (Critical)**: 立即修復,可繞過 CI (人工驗證)
- **P1 (High)**: 24h 內修復,必須通過 CI
- **P2 (Medium)**: 正常流程

---

## 7. 常見問題 (FAQ)

### ❓ **Q1: 我不小心在 main 分支上做了變更怎麼辦?**

```bash
# 方法 1: 移動到新分支 (未 commit 的情況)
git stash
git checkout -b feature/RA-XXX-my-changes
git stash pop

# 方法 2: 已 commit 但未 push
git log  # 記下 commit SHA
git reset --hard HEAD~1  # 撤銷最後一次 commit
git checkout -b feature/RA-XXX-my-changes
git cherry-pick <commit-sha>
```

### ❓ **Q2: 我的 Commit 訊息寫錯了怎麼辦?**

```bash
# 修改最後一次 commit 的訊息 (未 push 的情況)
git commit --amend -m "fix(api): correct commit message"

# 已經 push 的情況: 不建議修改,除非分支只有你在用
git commit --amend -m "fix(api): correct commit message"
git push --force-with-lease origin feature/RA-XXX  # 謹慎使用!
```

### ❓ **Q3: 我要如何刪除遠端分支?**

```bash
# 刪除遠端分支
git push origin --delete feature/RA-XXX-old-branch

# 清理本地已刪除的遠端分支追蹤
git fetch --prune
```

### ❓ **Q4: 我的分支落後 main 很多,應該 merge 還是 rebase?**

**原則**:
- ✅ **私有分支 (只有你在開發)**: 使用 `git rebase main` (保持歷史線性)
- ✅ **共享分支 (多人協作)**: 使用 `git merge main` (保留分支歷史)
- ✅ **團隊預設策略**: Rebase (RespiraAlly 專案)

```bash
# Rebase (推薦)
git checkout feature/RA-XXX
git rebase main

# Merge (多人協作時)
git checkout feature/RA-XXX
git merge main
```

### ❓ **Q5: CI 失敗了怎麼辦?**

```bash
# 1. 查看 GitHub Actions 錯誤訊息
# 2. 本地重現錯誤
uv run pytest  # 或其他失敗的檢查

# 3. 修復後重新提交
git add <fixed-files>
git commit -m "fix(ci): resolve failing tests"
git push origin feature/RA-XXX

# 4. GitHub Actions 會自動重新執行
```

### ❓ **Q6: 我要如何查看某個檔案的修改歷史?**

```bash
# 查看檔案的 commit 歷史
git log --follow --oneline backend/src/api/patients.py

# 查看某次 commit 對該檔案的修改
git show <commit-sha>:backend/src/api/patients.py

# 找出某行程式碼是誰寫的 (blame)
git blame backend/src/api/patients.py
```

---

## 8. 檢查清單 (Checklist)

### ✅ **每次提交前**
- [ ] `git status` 確認要提交的檔案
- [ ] `git diff` 檢查變更內容
- [ ] 執行 Linter (Black, Ruff, ESLint)
- [ ] 執行測試 (pytest, npm test)
- [ ] Commit 訊息符合 Conventional Commits 格式
- [ ] 不包含敏感資料 (.env, API keys)

### ✅ **建立 PR 前**
- [ ] 分支名稱符合命名規範
- [ ] 所有測試通過
- [ ] 已同步最新的 main 分支
- [ ] PR 描述清楚 (Summary, Changes, Test Plan)
- [ ] 已自我 Review 程式碼
- [ ] CI 檢查通過

### ✅ **Merge 前**
- [ ] 至少 1 個 Approve
- [ ] 所有 CI 檢查通過
- [ ] 無 Merge Conflict
- [ ] 已通知相關人員

---

## 9. 工具與資源

### 🔧 **推薦工具**

| 工具 | 用途 | 安裝指令 |
|------|------|----------|
| **GitHub CLI** | PR 管理 | `brew install gh` (Mac) / `sudo apt install gh` (Linux) |
| **tig** | Git 歷史瀏覽 | `brew install tig` / `sudo apt install tig` |
| **commitlint** | Commit 訊息驗證 | 見 1.4.4 任務 |
| **husky** | Git Hooks 管理 | 見 1.4.4 任務 |

### 📚 **參考資源**

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [01_development_workflow.md](./01_development_workflow.md)
- [RespiraAlly GitHub](https://github.com/kuku-rar/RespiraAlly_v2)

---

## 10. 變更記錄

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| v1.0 | 2025-10-18 | 初始版本 - 整合 01_development_workflow.md 規範 | Claude Code AI |

---

**核心哲學**: *"Talk is cheap. Show me the code."* - Linus Torvalds

**專案準則**: 流程服務工程,不是相反。簡單、實用、可驗證。

---

*此 SOP 遵循 Linus Torvalds 實用主義原則,確保團隊高效協作同時維持程式碼品質。*
