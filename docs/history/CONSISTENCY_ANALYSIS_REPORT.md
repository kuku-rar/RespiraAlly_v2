
# docs/ 資料夾一致性分析報告

**生成時間**: 2025-10-19 14:28:46
**分析範圍**: `/mnt/a/AIPE01_期末專題/RespiraAlly/docs`
**分析文件數**: 47 個 Markdown 文件

---

## 📊 執行摘要

### 總覽統計

| 指標 | 數量 | 說明 |
|------|------|------|
| 📄 總文件數 | 47 | 所有 Markdown 文件 |
| 📁 子資料夾數 | 9 | 包含 adr, ai, bdd, database 等 |
| 📝 有版本號 | 18 | 文件包含版本元數據 |
| 📅 有更新日期 | 18 | 文件包含最後更新日期 |
| ⚠️ 發現問題 | 36 | 需要修復或改進的項目 |

### 文件結構分布

```
docs/
├── 根目錄主文檔: 12 個 (00-17 系列)
├── adr/ (架構決策): 9 個
├── ai/ (AI 設計): 3 個
├── bdd/ (行為規範): 1 個
├── database/ (數據庫設計): 2 個
├── dev_logs/ (開發日誌): 7 個
├── frontend/ (前端文檔): 1 個
├── history/ (歷史備份): 6 個
├── project_management/ (專案管理): 5 個
└── security/ (安全設計): 1 個
```

---

## 🔴 Critical Issues (必須立即修復)

### 1. 版本衝突

**問題**: WBS 已更新到 v3.0（客戶新需求整合），但 PRD 仍為 v2.0

| 文件 | 當前版本 | 最後更新 | 狀態 |
|------|----------|----------|------|
| 16_wbs_development_plan.md | v3.0 | 2025-10-19 13:30 | ✅ 最新 |
| 02_product_requirements_document.md | v2.0 | 2025-10-17 | ❌ 需更新 |
| 05_architecture_and_design.md | v2.0 | 2025-10-19 | ⚠️ 待評估 |

**影響**:
- PRD 未反映客戶新需求（資料準確性驗證 + 營養評估 KPI）
- 開發團隊可能基於過時的需求進行實作
- 文檔版本不一致影響可追溯性

**建議修復方案**:
1. **立即更新 PRD 到 v3.0**:
   ```bash
   # 更新 PRD 以反映 WBS v3.0 的客戶新需求
   - 新增 Section: 病患資料準確性驗證需求
   - 新增 Section: 營養評估 KPI 需求 (4 核心指標)
   - 更新版本號: v2.0 → v3.0
   - 更新日期: 2025-10-17 → 2025-10-20
   ```

2. **評估架構文檔是否需要更新**:
   - 檢查 05_architecture_and_design.md 是否需要反映新需求的架構影響
   - 如果不需要架構變更，可保持 v2.0

---

### 2. 失效連結 (34 個)

**問題**: 多個文件引用的連結指向不存在的文件

#### 高頻失效連結（出現次數最多）

| 連結目標 | 出現次數 | 引用文件 |
|----------|----------|----------|
| `./history/architecture_review_2025-10-18.md` | 4 | 02_PRD, 05_Architecture (多處) |
| `./database/schema_design_v1.0.md` | 4 | 05_Architecture, 06_API |
| `./adr/001-modular-monolith-architecture.md` | 1 | 05_Architecture |
| `./adr/005-rabbitmq-message-queue.md` | 1 | 05_Architecture |

**根本原因分析**:

1. **文件重命名或移動**:
   - `history/architecture_review_2025-10-18.md` 可能已改名為 `history/architecture_review_2025-10-18.md`
   - `database/schema_design_v1.0.md` 可能已改名為 `database/schema_design_v1.0.md`

2. **ADR 命名不一致**:
   - 部分 ADR 使用 `001-xxx` 格式
   - 實際文件使用 `ADR-001-xxx` 格式

**建議修復方案**:

**方案 A: 批量更新連結路徑** (推薦)
```bash
# 更新所有失效連結到正確路徑
./history/architecture_review_2025-10-18.md → ./history/architecture_review_2025-10-18.md
./database/schema_design_v1.0.md → ./database/schema_design_v1.0.md
./adr/001-xxx.md → ./adr/ADR-001-xxx.md
```

**方案 B: 建立符號連結** (快速修復)
```bash
# 在 docs/ 根目錄建立符號連結
ln -s history/architecture_review_2025-10-18.md history/architecture_review_2025-10-18.md
ln -s database/schema_design_v1.0.md database/schema_design_v1.0.md
```

---

## 🟡 Warnings (建議修復)

### 1. 序號斷層

**問題**: 根目錄編號文件有斷層: [3, 4, 10, 13, 14, 15]

**現有文件**: 00, 01, 02, 05, 06, 07, 08, 09, 11, 12, 16, 17

**缺失編號分析**:

| 編號 | VibeCoding 模板對應 | 狀態 | 建議 |
|------|---------------------|------|------|
| 03 | BDD Guide | ❌ 不存在 | 已在 `bdd/` 子資料夾實現 |
| 04 | ADR Template | ❌ 不存在 | 已在 `adr/` 子資料夾實現 |
| 10 | Class Relationships | ❌ 不存在 | 待建立（如需要） |
| 13 | Security Checklist | ❌ 不存在 | 待建立（如需要） |
| 14 | Deployment Guide | ❌ 不存在 | 待建立（如需要） |
| 15 | Documentation Guide | ❌ 不存在 | 待建立（如需要） |

**建議**:
- **保持現狀**: 序號斷層是設計決策，BDD 和 ADR 已獨立到子資料夾
- **或**: 如果需要嚴格對齊 VibeCoding 模板，可建立對應文件

---

### 2. CHANGELOG 缺少版本號

**問題**: `dev_logs/CHANGELOG.md` 未在 header 提取到版本號

**原因**: CHANGELOG 使用條目式版本記錄，而非單一文件版本號

**建議**: 保持現狀，CHANGELOG 格式符合設計

---

## 🟢 Info (優化建議)

### 1. 文件元數據完整性

**當前狀態**: 18/47 文件有版本號與更新日期

**建議補充元數據的文件**:

```bash
# 優先補充核心文檔
- bdd/epic_*.feature 系列 (3 個)
- frontend/api_integration_guide.md
- dev_logs 子文檔（模板類）
```

**元數據標準格式**:
```markdown
**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `YYYY-MM-DD`
**主要作者 (Lead Author):** `作者名稱`
**審核者 (Reviewers):** `審核者名稱`
```

---

### 2. 備份文件管理

**問題**: `history/` 資料夾未清楚標註備份與當前文件的對應關係

**建議**:
1. **在 history/README.md 建立索引**:
   ```markdown
   # 歷史文件索引
   
   | 備份文件 | 對應當前文件 | 備份原因 | 備份日期 |
   |---------|-------------|---------|---------|
   | PRODUCT_REQUIREMENTS_DOCUMENT.md | 02_product_requirements_document.md | 重構前備份 | 2025-10-XX |
   ```

2. **定期清理過舊備份** (超過 30 天且無歷史價值)

---

## 🔧 修復腳本建議

### 腳本 1: 批量修復失效連結

```bash
#!/bin/bash
# fix_broken_links.sh

DOCS_DIR="/mnt/a/AIPE01_期末專題/RespiraAlly/docs"

# 定義連結替換規則
declare -A LINK_MAPPINGS=(
    ["./history/architecture_review_2025-10-18.md"]="./history/architecture_review_2025-10-18.md"
    ["./database/schema_design_v1.0.md"]="./database/schema_design_v1.0.md"
    ["./adr/001-modular-monolith-architecture.md"]="./adr/ADR-001-xxx.md"
)

# 批量替換
for old_link in "${!LINK_MAPPINGS[@]}"; do
    new_link="${LINK_MAPPINGS[$old_link]}"
    find "$DOCS_DIR" -name "*.md" -type f -exec sed -i "s|$old_link|$new_link|g" {} +
done

echo "✅ 失效連結已修復"
```

### 腳本 2: 更新 PRD 版本號

```bash
#!/bin/bash
# update_prd_version.sh

PRD_FILE="/mnt/a/AIPE01_期末專題/RespiraAlly/docs/02_product_requirements_document.md"

# 更新版本號
sed -i 's/v2.0/v3.0/g' "$PRD_FILE"

# 更新日期
sed -i 's/2025-10-17/2025-10-20/g' "$PRD_FILE"

echo "✅ PRD 版本已更新到 v3.0"
```

---

## 📋 改進計劃 (Action Items)

### Phase 1: 立即修復 (本週完成)

| 編號 | 任務 | 負責人 | 截止日期 | 狀態 |
|------|------|--------|----------|------|
| A1-1 | 更新 PRD 到 v3.0 (反映客戶新需求) | TaskMaster | 2025-10-20 | 🔲 |
| A1-2 | 批量修復 34 個失效連結 | TaskMaster | 2025-10-20 | 🔲 |
| A1-3 | 驗證所有連結可訪問性 | TaskMaster | 2025-10-20 | 🔲 |

### Phase 2: 短期改進 (下週完成)

| 編號 | 任務 | 負責人 | 截止日期 | 狀態 |
|------|------|--------|----------|------|
| A2-1 | 建立 history/README.md 索引 | TaskMaster | 2025-10-25 | 🔲 |
| A2-2 | 補充核心文檔元數據 | TaskMaster | 2025-10-25 | 🔲 |
| A2-3 | 定期一致性檢查 (每週一次) | TaskMaster | 持續 | 🔲 |

### Phase 3: 長期優化 (Sprint 1 完成前)

| 編號 | 任務 | 負責人 | 截止日期 | 狀態 |
|------|------|--------|----------|------|
| A3-1 | 建立自動化連結檢查 CI | TaskMaster | 2025-11-03 | 🔲 |
| A3-2 | 文檔版本同步策略 | TaskMaster | 2025-11-03 | 🔲 |
| A3-3 | 評估是否需要補充缺失編號文檔 | TaskMaster | 2025-11-03 | 🔲 |

---

## 📚 參考資源

### 相關文檔

- [VibeCoding Workflow Templates](../VibeCoding_Workflow_Templates/INDEX.md)
- [WBS Development Plan v3.0](./16_wbs_development_plan.md)
- [CHANGELOG v3.0](./dev_logs/CHANGELOG.md)

### 工具與腳本

- `docs_consistency_check.py`: 一致性分析腳本
- `fix_broken_links.sh`: 失效連結修復腳本（待建立）
- `update_prd_version.sh`: PRD 版本更新腳本（待建立）

---

**報告生成者**: TaskMaster Hub / Claude Code AI
**最後更新**: 2025-10-19 14:28:46
**文檔版本**: v1.0
