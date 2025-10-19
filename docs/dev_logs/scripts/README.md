# 開發日誌自動化腳本 (Dev Logs Automation Scripts)

**維護者**: TaskMaster Hub
**最後更新**: 2025-10-20

---

## 📚 腳本索引

### 1. generate_changelog.sh
**用途**: 從 git commits 自動生成 CHANGELOG 草稿

#### 使用方法

```bash
# 基本用法 (最近 7 天的 commits)
./docs/dev_logs/scripts/generate_changelog.sh v2.10

# 指定日期範圍
./docs/dev_logs/scripts/generate_changelog.sh v2.10 "2025-10-21" "2025-10-27"

# 使用相對日期
./docs/dev_logs/scripts/generate_changelog.sh v2.10 "7 days ago" "now"
```

#### 參數說明

| 參數 | 說明 | 預設值 | 範例 |
|------|------|--------|------|
| version | 版本號 | v2.x | v2.10 |
| start_date | 開始日期 | 7 days ago | 2025-10-21 |
| end_date | 結束日期 | now | 2025-10-27 |

#### 輸出內容

腳本會生成一個臨時草稿文件 `temp_changelog.md`,包含:

1. **Commits 統計**
   - 按 Conventional Commits 類型分組 (feat, fix, docs, etc.)
   - 每種類型的 commit 數量與列表

2. **文件變更統計**
   - 最近變更的文件列表
   - 每個 commit 的文件變更摘要

3. **代碼統計**
   - 變更文件數
   - 新增代碼行數
   - 刪除代碼行數
   - 淨增長行數

4. **可能的重要決策**
   - 從 commit message 中提取包含 "ADR", "Decision", "決策" 等關鍵字的 commits

5. **待補充資訊清單**
   - 提醒需要人工補充的資訊

#### 使用流程

```bash
# Step 1: 生成草稿
./docs/dev_logs/scripts/generate_changelog.sh v2.10 "2025-10-21" "2025-10-27"

# Step 2: 查看草稿
cat docs/dev_logs/scripts/temp_changelog.md

# Step 3: 編輯草稿 (補充詳細資訊)
vim docs/dev_logs/scripts/temp_changelog.md

# Step 4: 將草稿內容合併到 CHANGELOG.md
# (手動複製貼上到 CHANGELOG.md 的適當位置)

# Step 5: 刪除草稿
rm docs/dev_logs/scripts/temp_changelog.md
```

#### 注意事項

⚠️ **重要提醒**:

1. **僅供參考**: 生成的草稿僅供參考,需要人工審核與編輯
2. **人工補充**: 必須補充以下資訊:
   - 版本標題 (簡潔描述主要成就)
   - 階段與進度百分比
   - 工時變化計算
   - 完成的任務清單 (從 WBS 對照)
   - 主要交付物列表
   - 進度統計表格
   - 重要決策與變更說明
   - 里程碑標記
3. **遵循格式**: 合併到 CHANGELOG.md 時,請遵循現有格式
4. **時間倒序**: 新版本記錄應添加在最上方

---

## 🔧 未來可新增的腳本

### 2. generate_sprint_report.sh (待開發)
**用途**: 從 Sprint 日誌生成 Sprint 報告摘要

### 3. validate_logs.sh (待開發)
**用途**: 驗證開發日誌格式是否符合規範

### 4. sync_wbs_progress.sh (待開發)
**用途**: 從 git commits 同步更新 WBS 進度

---

## 📝 腳本開發指南

### 新增腳本流程

1. **建立腳本文件**
   ```bash
   touch docs/dev_logs/scripts/new_script.sh
   chmod +x docs/dev_logs/scripts/new_script.sh
   ```

2. **腳本基本結構**
   ```bash
   #!/bin/bash
   set -euo pipefail

   # 腳本說明
   # 用途: [描述腳本用途]
   # 使用方法: [使用方法]

   # 參數處理
   PARAM="${1:-default_value}"

   # 腳本邏輯
   echo "執行腳本..."

   # 錯誤處理
   if [ $? -ne 0 ]; then
       echo "❌ 錯誤: [錯誤訊息]"
       exit 1
   fi

   echo "✅ 完成"
   ```

3. **更新此 README**
   - 添加腳本到索引
   - 編寫使用說明
   - 提供範例

4. **測試腳本**
   ```bash
   # 測試腳本
   ./docs/dev_logs/scripts/new_script.sh

   # 驗證輸出
   ```

5. **提交到 git**
   ```bash
   git add docs/dev_logs/scripts/
   git commit -m "feat(scripts): add new_script.sh for [用途]"
   ```

### 腳本開發最佳實踐

1. **使用 set -euo pipefail**
   - 遇到錯誤立即退出
   - 未定義變數視為錯誤
   - 管道中任何命令失敗都會退出

2. **參數驗證**
   ```bash
   if [ $# -lt 1 ]; then
       echo "使用方法: $0 <param>"
       exit 1
   fi
   ```

3. **清楚的輸出訊息**
   ```bash
   echo "🔄 執行中..."
   echo "✅ 成功"
   echo "❌ 失敗"
   echo "⚠️ 警告"
   echo "💡 提示"
   ```

4. **錯誤處理**
   ```bash
   command || {
       echo "❌ 命令失敗"
       exit 1
   }
   ```

5. **相對路徑處理**
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   PROJECT_ROOT="$SCRIPT_DIR/../../.."
   ```

---

## 🔗 相關文件

- [開發日誌 CHANGELOG](../CHANGELOG.md)
- [Sprint 日誌模板](../sprint_logs/SPRINT_TEMPLATE.md)
- [會議記錄模板](../meetings/MEETING_TEMPLATE.md)
- [決策記錄模板](../decisions/DECISION_TEMPLATE.md)

---

**維護者**: TaskMaster Hub
**最後更新**: 2025-10-20
**文檔版本**: v1.0
