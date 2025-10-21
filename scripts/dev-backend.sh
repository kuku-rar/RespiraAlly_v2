#!/bin/bash
# RespiraAlly Backend Development Environment Launcher
# Author: TaskMaster Hub
# Last Updated: 2025-10-20

set -e

echo "🔵 切換到後端開發模式"
echo "================================"

# 切換到後端目錄
cd "$(dirname "$0")/../backend" || exit 1

# 啟動 Docker 服務
echo "📦 啟動 Docker 服務..."
docker-compose up -d postgres redis rabbitmq minio

# 等待服務就緒
echo "⏳ 等待服務啟動..."
sleep 3

# 檢查服務狀態
echo "✅ 檢查服務狀態..."
docker-compose ps

# 啟用 Python 虛擬環境
if [ -d ".venv" ]; then
    echo "🐍 啟用 Python 虛擬環境..."
    source .venv/bin/activate
else
    echo "⚠️  虛擬環境不存在，請先執行: uv sync"
fi

echo ""
echo "🎉 後端開發環境就緒！"
echo "================================"
echo "📍 API 文檔: http://localhost:8000/docs"
echo "🗄️  PostgreSQL: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo "🐰 RabbitMQ: http://localhost:15672"
echo "📦 MinIO: http://localhost:9001"
echo ""
echo "啟動開發伺服器: uvicorn respira_ally.main:app --reload"
echo ""
