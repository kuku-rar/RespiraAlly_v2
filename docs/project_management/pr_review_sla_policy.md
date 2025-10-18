# Pull Request Review SLA Policy

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-18`
**負責人 (Owner):** `Project Manager + Technical Lead`
**狀態 (Status):** `已批准 (Approved)`

---

## 目錄 (Table of Contents)

1. [SLA 承諾 (SLA Commitment)](#1-sla-承諾-sla-commitment)
2. [Review 優先級 (Priority Levels)](#2-review-優先級-priority-levels)
3. [Reviewer 責任分配 (Reviewer Assignment)](#3-reviewer-責任分配-reviewer-assignment)
4. [升級機制 (Escalation)](#4-升級機制-escalation)
5. [Review 標準 (Review Standards)](#5-review-標準-review-standards)
6. [度量指標 (Metrics)](#6-度量指標-metrics)

---

## 1. SLA 承諾 (SLA Commitment)

### 🎯 **核心 SLA 目標**

| 項目 | 目標 | 度量方式 |
|------|------|----------|
| **首次 Review 時間** | < 24 小時 | PR 建立時間 → 首個 Comment/Approve 時間 |
| **Approve 時間** | < 48 小時 | PR 建立時間 → Approve 時間 |
| **Merge 時間** | < 72 小時 | PR 建立時間 → Merge 時間 |
| **每週 PR Throughput** | > 5 PR/週 | 團隊平均 |

### ⏱️ **時間計算規則**

- ✅ **工作時間**: 週一至週五 09:00-18:00 (GMT+8)
- ✅ **假日排除**: 週末、國定假日不計入 SLA
- ✅ **暫停 SLA**:
  - PR 標記為 `draft` (草稿)
  - PR 有 Merge Conflict (作者需先解決)
  - PR 標記為 `on-hold` (需要等待某些條件)

**範例**:
```
PR 建立時間: 週五 17:00
首次 Review 目標: 週一 17:00 (24 工作小時)
```

---

## 2. Review 優先級 (Priority Levels)

### 🔥 **優先級定義**

| 優先級 | 標籤 | SLA | 適用情境 | 範例 |
|--------|------|-----|----------|------|
| **P0 (Critical)** | `priority:critical` | 4h | 生產環境緊急修復、嚴重安全問題 | Hotfix, 資料洩露修復 |
| **P1 (High)** | `priority:high` | 12h | 關鍵功能、阻塞其他開發 | Sprint 關鍵路徑任務 |
| **P2 (Normal)** | - | 24h | 一般功能開發、Bug 修復 | 新 API 端點, UI 調整 |
| **P3 (Low)** | `priority:low` | 48h | 文件更新、小重構 | README 更新, 註解修正 |

### 🏷️ **優先級判定**

```bash
# 建立 PR 時自動判定
gh pr create --label "priority:high"  # 手動標記

# 或在 PR 描述中使用關鍵字
# 標題包含 [HOTFIX] → P0
# 標題包含 [URGENT] → P1
# 預設 → P2
```

---

## 3. Reviewer 責任分配 (Reviewer Assignment)

### 👥 **Reviewer 角色**

| 角色 | 責任 | 人數 | 權重 |
|------|------|------|------|
| **Primary Reviewer** | 深度 Code Review,負責 Approve | 1 人 | 必須 |
| **Secondary Reviewer** | 可選的第二意見 | 0-1 人 | 可選 |
| **Domain Expert** | 特定領域專家 (AI/ML, Security) | 0-1 人 | 視需求 |

### 📋 **自動分配規則** (GitHub CODEOWNERS)

建立 `.github/CODEOWNERS` 檔案:

```
# Backend API
/backend/src/api/              @backend-lead
/backend/tests/                @backend-lead @qa-engineer

# Frontend
/frontend/dashboard/           @frontend-lead
/frontend/liff/                @frontend-lead

# AI/ML
/backend/src/ai/               @ai-ml-specialist
/backend/src/rag/              @ai-ml-specialist

# Infrastructure
/.github/workflows/            @devops-engineer
/docker-compose.yml            @devops-engineer

# Documentation
/docs/                         @technical-lead @product-manager

# Database
/backend/alembic/              @data-engineer @backend-lead
```

### 🔄 **輪流制度**

- ✅ **每週輪值**: Backend Lead, Frontend Lead 輪流擔任 Primary Reviewer
- ✅ **負載平衡**: 每人同時 Review 的 PR 不超過 3 個
- ✅ **休假備援**: 休假時指定代理人

---

## 4. 升級機制 (Escalation)

### ⚠️ **SLA 逾期處理**

#### **Level 1: 自動提醒 (Auto Reminder)**

```
時間點: SLA 剩餘 4h
動作: GitHub Actions 自動 Comment
訊息: "@reviewer-name 您有一個 PR 待 Review,SLA 剩餘 4 小時"
```

#### **Level 2: PM 介入 (PM Escalation)**

```
時間點: 超過 SLA 4h
動作: PM 收到通知,聯繫 Reviewer
訊息: "PR #123 已超過 SLA 4 小時,請優先處理"
負責人: Project Manager
```

#### **Level 3: TL 強制指派 (TL Override)**

```
時間點: 超過 SLA 12h
動作: Technical Lead 強制指派新 Reviewer
訊息: "原 Reviewer 無法回應,重新指派給 @new-reviewer"
負責人: Technical Lead
```

### 📊 **升級通知範本**

**GitHub Actions 自動 Comment**:
```markdown
⏰ **SLA Reminder**

Hi @reviewer-name, this PR has been waiting for review for **20 hours**.

- **SLA Target**: 24 hours (first review)
- **Time Remaining**: 4 hours
- **Priority**: Normal (P2)

Please review this PR or re-assign if you're unavailable. Thanks! 🙏
```

---

## 5. Review 標準 (Review Standards)

### ✅ **Review Checklist**

#### **1. 程式碼品質 (Code Quality)**
- [ ] 符合專案編碼風格 (Black, Ruff 通過)
- [ ] 無明顯的程式碼異味 (code smell)
- [ ] 適當的錯誤處理
- [ ] 無硬編碼的敏感資料
- [ ] 變數命名清楚有意義

#### **2. 功能正確性 (Functionality)**
- [ ] 符合 User Story 需求
- [ ] 邊界情況處理正確
- [ ] 無明顯的邏輯錯誤
- [ ] API 回應格式正確

#### **3. 測試覆蓋 (Test Coverage)**
- [ ] 新功能有對應的測試
- [ ] 測試涵蓋主要路徑和邊界情況
- [ ] 所有測試通過 (CI 綠燈)
- [ ] Mock/Stub 使用合理

#### **4. 文檔與註解 (Documentation)**
- [ ] 複雜邏輯有註解說明
- [ ] API 有 docstring
- [ ] README/文檔已更新 (如需要)
- [ ] CHANGELOG 已更新 (如需要)

#### **5. 安全性 (Security)**
- [ ] 無 SQL Injection 風險
- [ ] 無 XSS/CSRF 風險
- [ ] 敏感資料有適當加密/遮罩
- [ ] 權限檢查正確

#### **6. 效能 (Performance)**
- [ ] 無 N+1 查詢問題
- [ ] 大量數據有分頁處理
- [ ] 無不必要的計算或 I/O

### 🎯 **Review 回應範本**

#### **Approve 範本**:
```markdown
✅ **LGTM (Looks Good To Me)**

Reviewed and tested. Code quality is good, all checks passed.

**Highlights**:
- Clean implementation of patient list API
- Good test coverage (85%)
- Proper error handling

Approved! 🚀
```

#### **Request Changes 範本**:
```markdown
⚠️ **Changes Requested**

Thanks for the PR! A few items need addressing before approval:

**Critical**:
1. **Security**: Line 45 - User input not sanitized before SQL query
   - Recommendation: Use parameterized queries

**Major**:
2. **Error Handling**: Missing error handling for database connection failure
   - Recommendation: Add try-catch block

**Minor**:
3. **Code Style**: Variable name `x` on line 67 is not descriptive
   - Recommendation: Rename to `patient_count`

**Test**:
4. Missing test case for empty patient list scenario

Please address these items and ping me for re-review. Thanks! 🙏
```

---

## 6. 度量指標 (Metrics)

### 📊 **每週追蹤指標**

| 指標 | 目標 | 計算方式 | 負責人 |
|------|------|----------|--------|
| **首次 Review 時間** | < 24h (平均) | Σ(首次 Review 時間) / PR 數量 | PM |
| **Approve 時間** | < 48h (平均) | Σ(Approve 時間) / PR 數量 | PM |
| **PR Throughput** | > 5 PR/週 | 每週 Merge 的 PR 數量 | PM |
| **SLA 達成率** | > 90% | SLA 達成 PR 數 / 總 PR 數 | PM |
| **Review Comment 數** | 2-5 個/PR (平均) | Σ(Comment 數) / PR 數量 | TL |
| **CI Success Rate** | > 90% | CI 通過次數 / 總執行次數 | DevOps |

### 📈 **Dashboard 範例**

```markdown
## 本週 PR Review 指標 (2025-10-14 ~ 2025-10-18)

| 指標 | 目標 | 實際 | 狀態 |
|------|------|------|------|
| 首次 Review 時間 | < 24h | 18.5h | ✅ |
| Approve 時間 | < 48h | 42h | ✅ |
| PR Throughput | > 5 PR | 7 PR | ✅ |
| SLA 達成率 | > 90% | 85.7% | ⚠️ |

**分析**:
- ✅ 首次 Review 時間表現良好
- ⚠️ SLA 達成率略低,1 個 PR 超過 SLA (因 Reviewer 休假)
- 🎯 下週改進: 建立休假備援機制
```

---

## 7. 特殊情況處理

### 🚫 **Reviewer 無法回應**

**情境**: Reviewer 休假、生病、離職

**處理流程**:
1. ✅ Reviewer 提前在 GitHub Profile 設定 "Busy" 狀態
2. ✅ PM 重新指派給備援 Reviewer
3. ✅ 原 Reviewer 返回後接手後續維護

### 🔄 **大型 PR 處理**

**定義**: 變更 > 500 行程式碼

**特殊流程**:
1. ✅ 建議拆分成多個小 PR
2. ✅ 如無法拆分,允許多人 Review
3. ✅ SLA 延長至 48h (首次 Review)

### 🎯 **Trivial PR 快速通道**

**定義**: 變更 < 10 行,無邏輯變更 (如 README 修正)

**快速流程**:
1. ✅ 標記 `trivial` label
2. ✅ 只需 1 個 Approve (可為任何人)
3. ✅ 可自行 Merge (Self-Merge)

---

## 8. 工具與自動化

### 🤖 **GitHub Actions 自動化**

#### **自動 SLA 提醒**

建立 `.github/workflows/pr-sla-reminder.yml`:

```yaml
name: PR SLA Reminder

on:
  schedule:
    - cron: '0 */4 * * *'  # 每 4 小時執行一次

jobs:
  check-sla:
    runs-on: ubuntu-latest
    steps:
      - name: Check PR SLA
        uses: actions/github-script@v6
        with:
          script: |
            const prs = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open'
            });

            for (const pr of prs.data) {
              const createdAt = new Date(pr.created_at);
              const now = new Date();
              const hoursOpen = (now - createdAt) / (1000 * 60 * 60);

              // 24h SLA 警告
              if (hoursOpen > 20 && hoursOpen < 24) {
                await github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: pr.number,
                  body: `⏰ **SLA Reminder**: This PR has been open for ${hoursOpen.toFixed(1)} hours. First review SLA (24h) is approaching. @${pr.requested_reviewers[0]?.login || 'reviewer'}`
                });
              }

              // 24h SLA 超過
              if (hoursOpen > 24 && hoursOpen < 28) {
                await github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: pr.number,
                  body: `🚨 **SLA Exceeded**: This PR exceeded 24h SLA. Escalating to PM. @project-manager`
                });
                await github.rest.issues.addLabels({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: pr.number,
                  labels: ['sla-exceeded']
                });
              }
            }
```

### 📊 **週報自動生成**

```bash
# GitHub CLI 腳本 (週五執行)
gh pr list --state merged --json number,title,createdAt,mergedAt \
  --jq '.[] | select(.mergedAt | fromdateiso8601 > (now - 604800))' \
  > weekly_pr_report.json
```

---

## 9. 最佳實踐

### ✅ **作為 PR Author**

1. ✅ **Self-Review**: 提交前先自己 Review 一次
2. ✅ **小 PR**: 保持 PR < 300 行 (單一功能)
3. ✅ **描述清楚**: 使用 PR Template,說明 What/Why/How
4. ✅ **及時回應**: Reviewer 提出問題後 24h 內回應
5. ✅ **主動測試**: 在 PR 描述中附上測試結果

### ✅ **作為 Reviewer**

1. ✅ **及時 Review**: 收到指派後盡快開始 Review
2. ✅ **建設性意見**: 提出問題同時建議解法
3. ✅ **區分優先級**: Critical/Major/Minor 分類 Comment
4. ✅ **認可優點**: 對好的程式碼給予正面回饋
5. ✅ **深入理解**: 不確定時測試程式碼或詢問

---

## 10. 變更記錄

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|----------|------|
| v1.0 | 2025-10-18 | 初始版本 - 建立 PR Review SLA 政策 | Claude Code AI |

---

**核心原則**: *"Good code review is not about finding bugs. It's about sharing knowledge and maintaining standards."*

**團隊承諾**: 我們承諾在 24 小時內提供首次 Review,並持續追蹤 SLA 達成率。

---

*此政策遵循實用主義原則,平衡效率與品質,確保團隊協作順暢。*
