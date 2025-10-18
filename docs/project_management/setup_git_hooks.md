# Git Hooks 設置指南

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-18`
**負責人 (Owner):** `Technical Lead`

---

## 📋 概述

本專案使用 **commitlint + husky** 強制執行 [Conventional Commits](https://www.conventionalcommits.org/) 規範。

所有 commit 訊息必須符合以下格式，否則 commit 將被拒絕：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**範例**:
```
feat(api): add patient list endpoint

Implements GET /patients with pagination and filtering.

Resolves: RA-123
```

---

## 🚀 快速設置 (一次性操作)

### 前提條件

- ✅ Node.js >= 18.0.0
- ✅ npm >= 9.0.0

### 安裝步驟

```bash
# 1. 在專案根目錄安裝 npm 依賴
npm install

# 2. 初始化 husky (會自動執行 npm run prepare)
# 如果沒有自動執行,手動執行:
npx husky install

# 3. 驗證 hook 是否正確安裝
ls -la .husky/
# 應該看到 commit-msg 文件

# 4. 測試 commitlint
echo "test: this is a test" | npx commitlint
# 應該顯示 "⧗   input: test: this is a test"
```

---

## 📝 Commit 訊息規範

### Type (必填)

| Type | 用途 | 範例 |
|------|------|------|
| `feat` | 新功能 | `feat(api): add GET /patients endpoint` |
| `fix` | Bug 修復 | `fix(auth): resolve JWT expiry issue` |
| `docs` | 文件變更 | `docs(readme): update installation steps` |
| `style` | 格式調整 (不影響邏輯) | `style(api): format code with black` |
| `refactor` | 重構 | `refactor(db): simplify query logic` |
| `perf` | 效能優化 | `perf(api): add caching for patient list` |
| `test` | 測試 | `test(api): add unit tests for patients` |
| `build` | 建置系統 | `build(docker): update Dockerfile` |
| `ci` | CI/CD 配置 | `ci(github): add coverage reporting` |
| `chore` | 雜項 | `chore(deps): upgrade fastapi to 0.110` |
| `revert` | 回退 | `revert: revert "feat(api): add endpoint"` |

### Scope (可選,但推薦)

常用 scope:

- `api` - Backend API 變更
- `auth` - 認證/授權
- `db` - 資料庫
- `frontend` - 前端 (通用)
- `dashboard` - Next.js Dashboard
- `liff` - LINE LIFF App
- `ai` - AI/ML 元件
- `rag` - RAG 系統
- `ci` - CI/CD
- `docs` - 文件

### Subject (必填)

- ✅ 使用祈使句現在式 ("add" 而非 "added")
- ✅ 小寫開頭 (不用大寫)
- ✅ 不加句號
- ✅ 最多 72 字元

### Body (可選)

- 解釋 "為什麼" 而非 "是什麼"
- 每行最多 100 字元
- 可以有多行
- Body 前必須空一行

### Footer (可選)

- 連結 Issue: `Resolves: RA-123`
- 多個 Issue: `Resolves: RA-123, RA-124`
- 相關 Issue: `Related: RA-456`
- Breaking Change: `BREAKING CHANGE: <description>`

---

## ✅ Commit 訊息範例

### ✅ 正確範例

```bash
# 簡單 commit
git commit -m "feat(api): add patient list endpoint"

# 帶 body 和 footer
git commit -m "$(cat <<'EOF'
fix(auth): resolve JWT token expiry bug

The JWT tokens were not correctly validating the expiry time,
allowing expired tokens to authenticate. This fix adds proper
exp claim validation.

Resolves: RA-234
EOF
)"

# 多行 commit (使用 HEREDOC)
git commit -m "$(cat <<'EOF'
feat(dashboard): add patient dashboard view

- Implement patient list table with sorting
- Add filtering by status and risk level
- Add search functionality

Resolves: RA-345
EOF
)"
```

### ❌ 錯誤範例

```bash
# ❌ 缺少 type
git commit -m "add patient list"

# ❌ Type 大寫
git commit -m "Feat(api): add endpoint"

# ❌ Subject 大寫開頭
git commit -m "feat(api): Add endpoint"

# ❌ Subject 結尾有句號
git commit -m "feat(api): add endpoint."

# ❌ Subject 太長 (> 72 字元)
git commit -m "feat(api): add a very long endpoint that retrieves patient information with advanced filtering options"

# ❌ 無意義的訊息
git commit -m "fix: update"
git commit -m "feat: WIP"
git commit -m "chore: changes"
```

---

## 🔧 常見問題

### Q1: Commit hook 沒有執行怎麼辦?

```bash
# 檢查 husky 是否正確安裝
ls -la .git/hooks/
# 應該看到 commit-msg 符號連結到 .husky/commit-msg

# 如果沒有,重新安裝
npm run prepare

# 或手動執行
npx husky install
```

### Q2: 如何臨時跳過 commit hook?

```bash
# 不建議,但緊急情況可使用 --no-verify
git commit -m "emergency fix" --no-verify

# ⚠️ 警告: 這會跳過所有檢查,包括 commitlint 和 pre-commit hooks
# 請盡量遵循規範,避免使用此選項
```

### Q3: Commit 失敗並顯示 "commitlint not found"

```bash
# 確保已安裝 npm 依賴
npm install

# 檢查 commitlint 是否存在
npx commitlint --version
```

### Q4: 我想修改上一次的 commit 訊息

```bash
# 修改最後一次 commit (未 push 的情況)
git commit --amend -m "feat(api): correct commit message"

# 已經 push 的情況: 不建議修改
# 如果一定要修改 (僅限個人分支):
git commit --amend -m "feat(api): correct commit message"
git push --force-with-lease origin feature/RA-XXX
```

### Q5: 如何查看 commitlint 規則?

```bash
# 查看 commitlint 配置
cat commitlint.config.js

# 測試 commit 訊息
echo "feat(api): test message" | npx commitlint
```

---

## 🛠️ 手動測試

### 測試有效的 commit 訊息

```bash
echo "feat(api): add patient list endpoint" | npx commitlint
# ✅ 應該通過

echo "fix(auth): resolve token expiry" | npx commitlint
# ✅ 應該通過
```

### 測試無效的 commit 訊息

```bash
echo "add patient list" | npx commitlint
# ❌ 應該失敗: type-empty

echo "Feat(api): add endpoint" | npx commitlint
# ❌ 應該失敗: type-case

echo "feat(api): Add endpoint" | npx commitlint
# ❌ 應該失敗: subject-case
```

---

## 📊 整合 IDE

### VSCode

安裝 [Conventional Commits](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits) 擴展:

```json
// .vscode/settings.json
{
  "conventionalCommits.scopes": [
    "api",
    "auth",
    "db",
    "frontend",
    "dashboard",
    "liff",
    "ai",
    "ci",
    "docs"
  ]
}
```

### Git GUI 工具

大多數 Git GUI 工具 (如 GitKraken, SourceTree) 會自動執行 commit hooks。

---

## 🎯 最佳實踐

1. ✅ **Commit 頻繁**: 小步快跑,每個邏輯變更一個 commit
2. ✅ **訊息清晰**: 讓未來的你能快速理解變更
3. ✅ **連結 Issue**: 使用 `Resolves: RA-XXX` 建立追溯性
4. ✅ **使用 Scope**: 幫助快速識別變更範圍
5. ✅ **Body 說明**: 複雜變更加入 body 解釋原因

---

## 📚 參考資源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [commitlint Documentation](https://commitlint.js.org/)
- [husky Documentation](https://typicode.github.io/husky/)
- [Git Workflow SOP](./git_workflow_sop.md)

---

## 🔄 故障排除

### 完整重置流程

```bash
# 1. 刪除現有 node_modules (如果存在)
rm -rf node_modules package-lock.json

# 2. 重新安裝
npm install

# 3. 重新初始化 husky
npx husky install

# 4. 驗證
git commit --allow-empty -m "test(ci): test commitlint hook"
# 應該觸發 commitlint 驗證
```

---

**最後更新**: 2025-10-18
**維護者**: Technical Lead

*此文件遵循實用主義原則,確保團隊成員能快速設置並理解 Git Hooks。*
