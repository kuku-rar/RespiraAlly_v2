#!/bin/bash
# RespiraAlly Frontend Development Environment Launcher
# Author: TaskMaster Hub
# Last Updated: 2025-10-20

set -e

# 參數: dashboard 或 liff (預設 dashboard)
FRONTEND_APP="${1:-dashboard}"

echo "🟢 切換到前端開發模式: $FRONTEND_APP"
echo "================================"

# 切換到前端目錄
cd "$(dirname "$0")/../frontend/$FRONTEND_APP" || exit 1

# 設定環境變數
if [ "$FRONTEND_APP" = "dashboard" ]; then
    cat > .env.local <<EOF
# Dashboard Development Environment
NEXT_PUBLIC_MOCK_MODE=true
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
EOF
    echo "✅ 建立 .env.local (Mock 模式: 啟用)"
elif [ "$FRONTEND_APP" = "liff" ]; then
    cat > .env <<EOF
# LIFF Development Environment
VITE_MOCK_MODE=true
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_LIFF_ID=your-liff-id-here
EOF
    echo "✅ 建立 .env (Mock 模式: 啟用)"
fi

# 檢查依賴是否安裝
if [ ! -d "node_modules" ]; then
    echo "📦 安裝依賴套件..."
    npm install
fi

echo ""
echo "🎉 前端開發環境就緒！"
echo "================================"
if [ "$FRONTEND_APP" = "dashboard" ]; then
    echo "📍 Dashboard: http://localhost:3000"
    echo "🔧 Mock 模式: 已啟用"
    echo ""
    echo "啟動開發伺服器: npm run dev"
    echo "關閉 Mock 模式: echo 'NEXT_PUBLIC_MOCK_MODE=false' > .env.local"
else
    echo "📍 LIFF: http://localhost:5173"
    echo "🔧 Mock 模式: 已啟用"
    echo ""
    echo "啟動開發伺服器: npm run dev"
    echo "關閉 Mock 模式: echo 'VITE_MOCK_MODE=false' > .env"
fi
echo ""
