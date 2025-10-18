# 專案管理文檔索引 (Project Management Documentation)

**目錄位置**: `/docs/project_management/`
**最後更新**: 2025-10-18
**維護者**: Technical Lead, Project Manager

---

## 📚 文檔清單

本資料夾包含 RespiraAlly V2.0 專案的核心管理文檔，涵蓋開發流程、程式碼審查、品質管控等關鍵流程規範。

### 1. Git 工作流程規範 (Git Workflow SOP)

**檔案**: [`git_workflow_sop.md`](./git_workflow_sop.md)
**用途**: 定義統一的 Git 分支策略、Commit 規範、衝突解決流程
**適用對象**: 全體開發人員
**關鍵內容**:
- 🌿 分支命名規範 (`feature/`, `fix/`, `hotfix/` 等)
- 📝 Commit Message 格式 (Conventional Commits)
- 🔀 Merge 策略 (Squash and Merge)
- ⚠️ 衝突解決流程
- 🔥 Hotfix 緊急修復流程
- ❓ FAQ 常見問題

**依據規範**: [01_development_workflow.md](../01_development_workflow.md) §Ⅲ.1

---

### 2. PR 審查 SLA 政策 (PR Review SLA Policy)

**檔案**: [`pr_review_sla_policy.md`](./pr_review_sla_policy.md)
**用途**: 定義 Pull Request 審查的服務等級協議 (SLA) 與升級機制
**適用對象**: 全體開發人員、Code Reviewers
**關鍵內容**:
- 🎯 SLA 目標
  - 首次 Review: < 24 小時
  - Approve: < 48 小時
  - Merge: < 72 小時
- 📊 度量指標與追蹤方式
- ⏫ 升級機制 (Escalation Path)
- 🚀 最佳實踐與反模式
- 🏆 Reviewer 責任與權限

**依據規範**: [01_development_workflow.md](../01_development_workflow.md) §Ⅲ.5

---

### 3. Git Hooks 設置指南 (Git Hooks Setup Guide)

**檔案**: [`setup_git_hooks.md`](./setup_git_hooks.md)
**用途**: commitlint + husky 安裝與使用指南
**適用對象**: 全體開發人員 (必須執行一次性設置)
**關鍵內容**:
- 🚀 一次性安裝步驟 (npm install + husky install)
- 📝 Commit Message 規範速查表
- ✅ 有效/無效 Commit 範例
- 🔧 故障排除 (Troubleshooting)
- 🛠️ 手動測試指令
- 💡 IDE 整合 (VSCode Conventional Commits 擴展)

**依據規範**: [01_development_workflow.md](../01_development_workflow.md) §Ⅲ.4

---

## 🔗 相關文檔

| 文檔 | 路徑 | 說明 |
|------|------|------|
| **開發工作流程規範** | [`../01_development_workflow.md`](../01_development_workflow.md) | 開發流程總規範 (母文檔) |
| **WBS 開發計畫** | [`../16_wbs_development_plan.md`](../16_wbs_development_plan.md) | 專案 WBS 與時程規劃 |
| **PR Template** | [`../../.github/pull_request_template.md`](../../.github/pull_request_template.md) | GitHub PR 描述模板 |
| **CI 配置** | [`../../.github/workflows/ci.yml`](../../.github/workflows/ci.yml) | GitHub Actions CI/CD Quality Gates |
| **commitlint 配置** | [`../../commitlint.config.js`](../../commitlint.config.js) | Commit 訊息驗證規則 |

---

## 📖 使用流程

### 新成員 Onboarding

1. **閱讀順序**:
   ```
   1. git_workflow_sop.md (30 分鐘)
   2. setup_git_hooks.md (執行設置 10 分鐘)
   3. pr_review_sla_policy.md (15 分鐘)
   ```

2. **設置檢查清單**:
   - [ ] 閱讀 Git Workflow SOP
   - [ ] 執行 `npm install` 安裝 commitlint + husky
   - [ ] 測試 commit hook: `echo "test: validate hook" | npx commitlint`
   - [ ] 建立第一個分支: `git checkout -b feature/RA-XXX-test`
   - [ ] 提交第一個符合規範的 commit
   - [ ] 閱讀 PR SLA 政策,了解審查時效

### 日常開發

- **開始新功能前**: 檢查分支命名是否符合 `feature/RA-XXX-description` 格式
- **提交 Commit 時**: 確保符合 `<type>(<scope>): <subject>` 格式
- **建立 PR 時**: 填寫 PR Template,指定 Reviewer
- **審查 PR 時**: 遵守 24h SLA,使用 GitHub Suggestions

---

## 🎯 品質檢核點

所有開發流程必須通過以下檢核點:

### Git Commit 檢核
- ✅ Commit 訊息符合 Conventional Commits
- ✅ Commit hook (commitlint) 驗證通過
- ✅ 每個 commit 原子性 (單一邏輯變更)

### PR 檢核
- ✅ PR 描述完整 (使用 Template)
- ✅ 首次 Review < 24h
- ✅ 所有 Reviewer Approve
- ✅ CI Quality Gates 全部通過
- ✅ 衝突已解決

### CI/CD 檢核 (Quality Gates)
- ✅ **Backend**: Black (format) + Ruff (lint) + Mypy (types) + Pytest (coverage ≥ 80%)
- ✅ **Frontend**: Prettier (format) + ESLint (lint) + TypeScript (types) + Build

---

## 📊 度量指標

專案管理流程的健康度透過以下指標追蹤:

| 指標 | 目標 | 追蹤方式 |
|------|------|----------|
| PR 首次 Review 時間 | < 24h | GitHub Insights |
| PR 平均 Merge 時間 | < 72h | GitHub Insights |
| Commit 規範合規率 | 100% | commitlint 報告 |
| CI 成功率 | > 95% | GitHub Actions Dashboard |
| PR Throughput | > 5 PR/週 | GitHub Insights |

---

## 🚨 緊急處理

### Hotfix 流程
1. 參考 [`git_workflow_sop.md`](./git_workflow_sop.md) §Ⅵ Hotfix 流程
2. 建立 `hotfix/RA-XXX-description` 分支
3. 修復後立即 PR,優先審查 (2h SLA)
4. Merge 後立即部署與驗證

### PR 積壓處理
- 參考 [`pr_review_sla_policy.md`](./pr_review_sla_policy.md) §Ⅳ 升級機制
- 超過 24h 無 Review → 通知 TL
- 超過 48h 無 Approve → 通知 PM 協調資源

---

## 📝 文檔維護

- **更新頻率**: 每 Sprint 結束後檢視
- **變更流程**: 透過 PR 修改,經 TL 批准
- **版本管理**: 文檔變更遵循 Conventional Commits (`docs(pm): update workflow`)

---

**建立日期**: 2025-10-18
**對應 WBS**: 1.4 開發流程管控
**依據規範**: 01_development_workflow.md

*此資料夾為 RespiraAlly V2.0 專案管理核心文檔集,確保開發流程規範化與可追溯性。*
