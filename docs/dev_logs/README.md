# 開發日誌 (Development Logs)

**專案**: RespiraAlly V2.0
**維護者**: TaskMaster Hub / Claude Code AI
**最後更新**: 2025-10-20

---

## 📚 文件索引

### 📂 資料夾結構

```
dev_logs/
├── CHANGELOG.md              # 完整開發日誌 (v2.0-v2.9)
├── README.md                 # 本文件 (索引與維護指南)
├── sprint_logs/              # Sprint 回顧日誌
│   ├── SPRINT_TEMPLATE.md    # Sprint 日誌模板
│   └── sprint_1_retrospective.md  # Sprint 1 回顧 (預建立)
├── meetings/                 # 會議記錄
│   └── MEETING_TEMPLATE.md   # 會議記錄模板
├── decisions/                # 開發決策日誌
│   └── DECISION_TEMPLATE.md  # 決策記錄模板
└── scripts/                  # 自動化腳本
    ├── README.md             # 腳本使用說明
    └── generate_changelog.sh # CHANGELOG 自動生成腳本
```

### 核心文件

1. **[CHANGELOG.md](./CHANGELOG.md)** - 完整開發日誌
   - 所有版本的詳細變更記錄 (v2.0 - v2.9)
   - 架構決策變更追蹤
   - 工時調整與進度更新
   - 交付物清單

### Sprint 日誌

2. **[sprint_logs/SPRINT_TEMPLATE.md](./sprint_logs/SPRINT_TEMPLATE.md)** - Sprint 回顧模板
   - Sprint 概覽與目標達成狀況
   - 完成/未完成任務清單
   - 指標與數據統計
   - 經驗教訓與改進建議

3. **[sprint_logs/sprint_1_retrospective.md](./sprint_logs/sprint_1_retrospective.md)** - Sprint 1 回顧
   - 預建立的 Sprint 1 日誌
   - 在 Sprint 執行過程中持續更新
   - Sprint 結束時完成填寫

### 會議記錄

4. **[meetings/MEETING_TEMPLATE.md](./meetings/MEETING_TEMPLATE.md)** - 會議記錄模板
   - 適用於各類會議 (Planning, Review, Retro, Daily Standup, Technical Discussion)
   - 議程、決策、行動項記錄
   - 阻塞與風險追蹤

### 開發決策

5. **[decisions/DECISION_TEMPLATE.md](./decisions/DECISION_TEMPLATE.md)** - 開發決策模板
   - 日常開發決策記錄 (非正式 ADR)
   - 方案比較與選擇理由
   - 實施計劃與成功標準
   - 風險與緩解措施

### 自動化腳本

6. **[scripts/generate_changelog.sh](./scripts/generate_changelog.sh)** - CHANGELOG 自動生成
   - 從 git commits 生成 CHANGELOG 草稿
   - 統計 commits、文件變更、代碼增刪
   - 提取可能的重要決策
   - 使用說明: [scripts/README.md](./scripts/README.md)

---

## 📖 閱讀指南

### 快速查找

#### 查看最新變更
```bash
# 查看最新版本
head -n 200 CHANGELOG.md
```

#### 查找特定版本
```bash
# 查找 v2.9 版本記錄
grep -A 50 "## v2.9" CHANGELOG.md
```

#### 查找特定關鍵字
```bash
# 查找 JWT 相關變更
grep -i "jwt" CHANGELOG.md

# 查找索引相關變更
grep -i "index" CHANGELOG.md
```

### 版本記錄結構

每個版本記錄包含:

```markdown
## vX.X (YYYY-MM-DD) - 標題

**階段**: Sprint X (XX%)
**工時**: +XXh (總計 XXXh)

### ✅ 完成的任務
### 📊 進度更新
### 📦 交付物
### 🎯 里程碑
```

---

## 🔄 維護流程

### 新增版本記錄 (CHANGELOG)

1. **使用自動化腳本生成草稿** (推薦):
   ```bash
   # 生成最近 7 天的變更草稿
   ./docs/dev_logs/scripts/generate_changelog.sh v2.10

   # 查看草稿
   cat docs/dev_logs/scripts/temp_changelog.md
   ```

2. **手動編輯 CHANGELOG.md**:
   ```bash
   cd docs/dev_logs
   vim CHANGELOG.md
   ```

3. **在目錄後新增版本**:
   - 使用一致的格式
   - 保持時間倒序 (最新在上)
   - 更新目錄索引

4. **記錄必要資訊**:
   - 版本號與日期
   - 階段與進度百分比
   - 工時變化 (+XXh)
   - 完成的任務清單
   - 進度統計表格
   - 交付物列表

5. **提交到 Git**:
   ```bash
   git add docs/dev_logs/CHANGELOG.md
   git commit -m "docs(changelog): add vX.X release notes"
   ```

### 記錄 Sprint 回顧

1. **Sprint 開始時**:
   ```bash
   # 如果尚未建立,複製模板
   cp docs/dev_logs/sprint_logs/SPRINT_TEMPLATE.md \
      docs/dev_logs/sprint_logs/sprint_X_retrospective.md

   # 填寫基本資訊
   vim docs/dev_logs/sprint_logs/sprint_X_retrospective.md
   ```

2. **Sprint 執行過程中**:
   - 在 "Sprint 執行日誌" 區塊記錄每日/每週重要事項
   - 遇到問題時記錄在 "遇到的問題" 區塊

3. **Sprint 結束時**:
   - 完成所有待更新區塊
   - 填寫完成/未完成任務清單
   - 記錄指標與數據
   - 在 Review/Retro 會議中討論並記錄經驗教訓

4. **提交到 Git**:
   ```bash
   git add docs/dev_logs/sprint_logs/sprint_X_retrospective.md
   git commit -m "docs(sprint): complete sprint X retrospective"
   ```

### 記錄會議

1. **會議前**:
   ```bash
   # 複製模板
   cp docs/dev_logs/meetings/MEETING_TEMPLATE.md \
      docs/dev_logs/meetings/sprint_X_planning.md

   # 填寫會議基本資訊與議程
   vim docs/dev_logs/meetings/sprint_X_planning.md
   ```

2. **會議中**:
   - 記錄討論內容
   - 記錄決策
   - 記錄行動項

3. **會議後**:
   - 審核會議記錄
   - 分發給參與者
   - 追蹤行動項執行

4. **提交到 Git**:
   ```bash
   git add docs/dev_logs/meetings/sprint_X_planning.md
   git commit -m "docs(meeting): add sprint X planning notes"
   ```

### 記錄開發決策

1. **遇到需要決策的問題時**:
   ```bash
   # 複製模板
   cp docs/dev_logs/decisions/DECISION_TEMPLATE.md \
      docs/dev_logs/decisions/DD-001_use_redis_for_cache.md

   # 填寫決策記錄
   vim docs/dev_logs/decisions/DD-001_use_redis_for_cache.md
   ```

2. **決策流程**:
   - 提議階段: 狀態設為 📋 提議
   - 討論階段: 記錄不同方案與觀點,狀態設為 ⏳ 討論中
   - 決策階段: 記錄最終決策與理由,狀態設為 ✅ 已接受
   - 實施階段: 追蹤行動項執行
   - 回顧階段: 定期回顧決策是否達到預期

3. **決策編號規則**:
   - 格式: `DD-XXX` (Development Decision)
   - 從 DD-001 開始遞增
   - 範例: DD-001, DD-002, DD-003

4. **提交到 Git**:
   ```bash
   git add docs/dev_logs/decisions/DD-XXX_*.md
   git commit -m "docs(decision): add DD-XXX [決策標題]"
   ```

### 更新索引

如果新增其他日誌文件,請更新本 README.md 的文件索引。

---

## 📊 版本記錄統計

| 版本 | 日期 | 階段 | 工時變化 | 主要成就 |
|------|------|------|----------|----------|
| v2.9 | 2025-10-20 | Sprint 0 (60.6%) | +8h | JWT 認證設計 + 索引策略規劃完成 |
| v2.8 | 2025-10-19 | Sprint 0 (55.3%) | - | 架構文件邏輯結構優化 |
| v2.5 | 2025-10-18 | Sprint 0 (41.7%) | +4h | AI 處理日誌設計完成 |
| v2.4 | 2025-10-18 | Sprint 0 (39.7%) | +8h | DDD 戰略設計完成 |
| v2.3 | 2025-10-18 | Sprint 0 (35.7%) | - | Git Hooks 修復完成 |
| v2.2 | 2025-10-18 | Sprint 0 (35.7%) | - | 開發流程管控完成 |
| v2.1 | 2025-10-18 | Sprint 0 (31%) | +71h | 專案管理流程重構 |
| v2.0 | 2025-10-18 | Sprint 0 | -24h | 架構重大調整 (MongoDB→PG) |

---

## 🔗 相關文件

### 專案管理
- [WBS 開發計劃](../16_wbs_development_plan.md) - 工作分解結構與進度追蹤
- [專案管理文檔](../project_management/README.md) - Git/PR/CI 流程規範

### 架構設計
- [系統架構設計](../05_architecture_and_design.md) - C4 模型、DDD 戰略設計
- [數據庫設計](../database/schema_design_v1.0.md) - Schema 與索引策略

### 安全設計
- [JWT 認證設計](../security/jwt_authentication_design.md) - 認證授權完整設計

### AI 設計
- [AI 處理日誌設計](../ai/21_ai_processing_logs_design.md) - STT/LLM/TTS 日誌追蹤

---

## 📝 記錄原則

### DO ✅

- 記錄重大架構決策與變更理由
- 記錄工時調整與原因
- 記錄進度里程碑
- 連結到詳細設計文檔
- 使用一致的 Markdown 格式
- 保持簡潔明瞭

### DON'T ❌

- 不記錄過度詳細的技術細節 (應在設計文檔中)
- 不記錄日常瑣碎任務
- 不使用不一致的格式
- 不遺漏工時變化記錄
- 不省略交付物清單

---

**維護者**: TaskMaster Hub
**最後更新**: 2025-10-20
**文檔版本**: v1.0
