#!/bin/bash
set -euo pipefail

# CHANGELOG 自動化生成腳本
# 用途: 從 git commits 生成 CHANGELOG 草稿
# 使用方法: ./generate_changelog.sh [version] [start_date] [end_date]
# 範例: ./generate_changelog.sh v2.10 2025-10-21 2025-10-27

VERSION="${1:-v2.x}"
START_DATE="${2:-7 days ago}"
END_DATE="${3:-now}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHANGELOG_FILE="$SCRIPT_DIR/../CHANGELOG.md"
TEMP_FILE="$SCRIPT_DIR/temp_changelog.md"

echo "🔄 生成 CHANGELOG 草稿..."
echo "版本: $VERSION"
echo "時間範圍: $START_DATE ~ $END_DATE"
echo ""

# 取得 git commits
echo "## $VERSION ($(date +%Y-%m-%d)) - [標題待補充]" > "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "**標題**: 待補充" >> "$TEMP_FILE"
echo "**階段**: Sprint X (XX%)" >> "$TEMP_FILE"
echo "**工時**: +XXh (總計 XXXh)" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "### ✅ 完成的任務" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 統計 commit 類型
echo "#### Commits 統計" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 按 Conventional Commits 類型分組
for type in feat fix docs style refactor perf test build ci chore; do
    commits=$(git log --since="$START_DATE" --until="$END_DATE" --oneline --grep="^$type:" || true)
    if [ -n "$commits" ]; then
        count=$(echo "$commits" | wc -l)
        echo "**$type** ($count commits):" >> "$TEMP_FILE"
        echo '```' >> "$TEMP_FILE"
        echo "$commits" >> "$TEMP_FILE"
        echo '```' >> "$TEMP_FILE"
        echo "" >> "$TEMP_FILE"
    fi
done

# 列出所有 commits
echo "#### 所有 Commits" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo '```' >> "$TEMP_FILE"
git log --since="$START_DATE" --until="$END_DATE" --oneline >> "$TEMP_FILE"
echo '```' >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 統計文件變更
echo "#### 文件變更統計" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo '```' >> "$TEMP_FILE"
git log --since="$START_DATE" --until="$END_DATE" --stat --oneline | tail -n 5 >> "$TEMP_FILE"
echo '```' >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 統計代碼增刪
echo "#### 代碼統計" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
git log --since="$START_DATE" --until="$END_DATE" --shortstat --oneline | \
    awk '/files? changed/ {files+=$1; inserted+=$4; deleted+=$6} END {
        print "- 變更文件數: " files " 個"
        print "- 新增代碼: " inserted " 行"
        print "- 刪除代碼: " deleted " 行"
        print "- 淨增長: " (inserted - deleted) " 行"
    }' >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 提取關鍵決策 (從 commit message 中找到 ADR, Decision 等關鍵字)
echo "#### 可能的重要決策 (需人工確認)" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
git log --since="$START_DATE" --until="$END_DATE" --oneline --grep="ADR\|Decision\|決策" >> "$TEMP_FILE" || echo "無" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 生成待辦事項
echo "---" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "### 📝 待補充資訊" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
echo "- [ ] 更新版本標題" >> "$TEMP_FILE"
echo "- [ ] 填寫階段與進度百分比" >> "$TEMP_FILE"
echo "- [ ] 計算工時變化" >> "$TEMP_FILE"
echo "- [ ] 整理完成的任務清單" >> "$TEMP_FILE"
echo "- [ ] 記錄主要交付物" >> "$TEMP_FILE"
echo "- [ ] 更新進度統計表格" >> "$TEMP_FILE"
echo "- [ ] 記錄重要決策與變更" >> "$TEMP_FILE"
echo "- [ ] 添加里程碑標記" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

echo "---" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

echo "✅ CHANGELOG 草稿已生成: $TEMP_FILE"
echo ""
echo "📋 下一步:"
echo "1. 查看草稿: cat $TEMP_FILE"
echo "2. 編輯草稿,補充必要資訊"
echo "3. 手動將草稿內容合併到 CHANGELOG.md"
echo "4. 刪除草稿: rm $TEMP_FILE"
echo ""
echo "💡 提示:"
echo "- 此草稿僅供參考,需要人工審核與編輯"
echo "- 請根據實際情況補充詳細資訊"
echo "- 遵循 CHANGELOG.md 現有格式"
