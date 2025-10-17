#!/bin/bash

# TaskMaster Post Write Hook
# 當 Claude Code 寫入檔案後觸發，特別關注文檔生成
# 透過 stdin 接收 JSON 格式的 tool 資料

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$CLAUDE_DIR/hooks.log"
}

log "🪝 TaskMaster Post Write Hook 觸發"

# 讀取 stdin 的 JSON 資料
if command -v jq >/dev/null 2>&1; then
    # 使用 jq 解析 JSON
    JSON_INPUT=$(cat)

    # 除錯模式：記錄原始 JSON
    if [ "$TASKMASTER_DEBUG" = "true" ]; then
        log "🔍 除錯模式: 收到的 JSON 資料長度: ${#JSON_INPUT} bytes"
        echo "--- RAW JSON START ---" >> "$CLAUDE_DIR/hooks.log"
        echo "$JSON_INPUT" >> "$CLAUDE_DIR/hooks.log"
        echo "--- RAW JSON END ---" >> "$CLAUDE_DIR/hooks.log"
    fi

    if [ ${#JSON_INPUT} -eq 0 ]; then
        log "⚠️ stdin 為空，未收到 JSON 資料"
        exit 0
    fi

    # 提取檔案路徑（從 tool_input 或 tool_response）
    FILE_PATH=$(echo "$JSON_INPUT" | jq -r '.tool_input.file_path // .tool_response.filePath // empty')

    if [ -z "$FILE_PATH" ]; then
        log "⚠️ 警告: 無法從 JSON 中提取檔案路徑"
        exit 0
    fi

    log "✅ 檔案路徑: $FILE_PATH"

else
    # 如果沒有 jq，使用 Python 解析
    log "ℹ️ 使用 Python 解析 JSON（jq 未安裝）"

    JSON_INPUT=$(cat)

    # 除錯模式：記錄原始 JSON
    if [ "$TASKMASTER_DEBUG" = "true" ]; then
        log "🔍 除錯模式: 收到的 JSON 資料長度: ${#JSON_INPUT} bytes"
        echo "--- RAW JSON START ---" >> "$CLAUDE_DIR/hooks.log"
        echo "$JSON_INPUT" >> "$CLAUDE_DIR/hooks.log"
        echo "--- RAW JSON END ---" >> "$CLAUDE_DIR/hooks.log"
    fi

    if [ ${#JSON_INPUT} -eq 0 ]; then
        log "⚠️ stdin 為空，未收到 JSON 資料"
        exit 0
    fi

    # 使用 Python 從 stdin 直接讀取，避免 shell 變數轉義問題
    FILE_PATH=$(echo "$JSON_INPUT" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    file_path = data.get('tool_input', {}).get('file_path') or data.get('tool_response', {}).get('filePath', '')
    print(file_path)
except Exception as e:
    sys.stderr.write(f'Python parsing error: {e}\n')
    sys.exit(1)
" 2>&1)

    if [ -z "$FILE_PATH" ]; then
        log "⚠️ 警告: 無法從 JSON 中提取檔案路徑"
        exit 0
    fi

    log "✅ 檔案路徑: $FILE_PATH"
fi

# 檢查是否為文檔檔案
if [[ "$FILE_PATH" == *.md ]]; then
    log "📄 偵測到 Markdown 文檔寫入: $FILE_PATH"

    # 檢查是否為專案文檔目錄
    if [[ "$FILE_PATH" == *"docs/"* ]]; then
        log "📋 專案文檔更新: $FILE_PATH"

        # 如果 TaskMaster 已初始化，通知文檔生成完成
        if [ -f "$CLAUDE_DIR/taskmaster-data/project.json" ]; then
            log "🔔 通知 TaskMaster 文檔生成完成"

            # 觸發文檔生成完成處理
            if [ -f "$CLAUDE_DIR/taskmaster.js" ]; then
                cd "$PROJECT_ROOT"
                node "$CLAUDE_DIR/taskmaster.js" --hook-trigger=document-generated --file="$FILE_PATH" || true
            fi

            # 顯示駕駛員審查提示
            cat << EOF

┌──────────────────────────────────────────────────────────┐
│  📄 文檔生成完成通知                                      │
│                                                          │
│  檔案: $(basename "$FILE_PATH")
│  路徑: $FILE_PATH
│                                                          │
│  🔍 駕駛員審查檢查點                                      │
│  請檢查生成的文檔內容，確認品質後：                      │
│                                                          │
│  ✅ 批准: /task-review approve                           │
│  🔄 修改: /task-review revise                            │
│  ⏸️ 暫停: /task-review pause                             │
│                                                          │
└──────────────────────────────────────────────────────────┘

EOF
        fi
    fi

    # 檢查是否為 VibeCoding 範本更新
    if [[ "$FILE_PATH" == *"VibeCoding_Workflow_Templates"* ]]; then
        log "🎨 VibeCoding 範本更新: $FILE_PATH"

        # 如果 TaskMaster 已初始化，可能需要重新評估任務
        if [ -f "$CLAUDE_DIR/taskmaster-data/project.json" ]; then
            log "🔄 範本更新，可能需要重新評估任務"
        fi
    fi
fi

# 檢查是否為 TaskMaster 核心檔案更新
if [[ "$FILE_PATH" == *".claude/taskmaster"* ]]; then
    log "🔧 TaskMaster 核心檔案更新: $FILE_PATH"
fi

# 檢查是否為 hooks 配置更新
if [[ "$FILE_PATH" == *"hooks-config.json"* ]] || [[ "$FILE_PATH" == *"settings.local.json"* ]]; then
    log "⚙️ Hooks 配置檔案更新: $FILE_PATH"
fi

log "✅ Post Write Hook 處理完成"
exit 0
