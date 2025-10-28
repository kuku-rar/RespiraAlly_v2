# RespiraAlly Docker 部署指南

本專案使用 Docker Compose 統一管理所有服務，包含前端、後端和基礎設施。

## 📋 目錄結構

```
RespiraAlly/
├── docker-compose.yml          # 基礎設施配置（PostgreSQL, Redis, RabbitMQ）
├── docker-compose.dev.yml      # 開發環境配置（使用 development schema）
├── docker-compose.prod.yml     # 生產環境配置（使用 production schema）
├── backend/
│   ├── Dockerfile             # Backend 容器配置
│   └── .dockerignore          # Backend 忽略檔案
├── frontend/
│   ├── dashboard/
│   │   ├── Dockerfile         # Dashboard 容器配置
│   │   └── .dockerignore
│   └── liff/
│       ├── Dockerfile         # LIFF 容器配置
│       ├── nginx.conf         # LIFF Nginx 配置
│       └── .dockerignore
└── .env                       # 環境變數配置
```

## 🔄 開發 vs 生產環境

本專案採用多檔案 Docker Compose 配置，支持開發和生產兩種環境，**最重要的差異是數據庫 Schema 分離**：

### 環境差異對比

| 特性 | 開發環境 (dev) | 生產環境 (prod) |
|------|---------------|----------------|
| **數據庫 Schema** | `development` | `production` |
| **熱重載 (Hot Reload)** | ✅ 啟用 | ❌ 停用 |
| **代碼掛載 (Volume Mount)** | ✅ 掛載本地代碼 | ❌ 使用構建映像 |
| **日誌級別** | DEBUG | INFO |
| **Worker 數量** | 1 (單進程) | 4 (多進程) |
| **資源限制** | ❌ 無限制 | ✅ CPU/Memory 限制 |
| **CORS 設置** | 寬鬆 (localhost) | 嚴格 (僅允許域名) |

### 為什麼要分離 Schema？

1. **數據隔離**：開發測試不會影響生產數據
2. **安全性**：生產數據完全隔離，防止誤操作
3. **測試自由**：可以任意創建/刪除/修改開發數據
4. **遷移測試**：可以在 development schema 先測試數據庫遷移

### Schema 切換方式

通過環境變數 `DB_SCHEMA` 控制使用哪個 Schema：
- **開發環境**: `DB_SCHEMA=development` → 存取 `development.patient_profiles` 等表
- **生產環境**: `DB_SCHEMA=production` → 存取 `production.patient_profiles` 等表

## 🚀 快速開始

### 1. 環境準備

確保已安裝：
- Docker Desktop (建議 24.0+)
- Docker Compose (v2.0+)

檢查版本：
```bash
docker --version
docker-compose --version
```

### 2. 環境變數設定

創建 `.env` 檔案（如果不存在）：
```bash
cp .env.example .env
```

編輯 `.env` 並設定必要的變數：
```env
# Database
POSTGRES_USER=admin
POSTGRES_PASSWORD=copd_secure_2024
POSTGRES_DB=respirally_db

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_PORT=5672

# LINE LIFF (選填)
LINE_LIFF_ID=your_liff_id_here

# LIFF Mock Mode
VITE_MOCK_MODE=false
```

### 3. 啟動服務

本專案使用分離的 Docker Compose 配置，支持開發和生產兩種環境：

**開發環境 (Development) - 推薦用於本地開發**：
```bash
# 啟動所有服務（基礎設施 + 前後端）- 使用 development schema
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 查看日誌
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# 停止服務
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

**生產環境 (Production)**：
```bash
# 啟動所有服務（基礎設施 + 前後端）- 使用 production schema
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 查看日誌
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# 停止服務
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

**只啟動基礎設施（資料庫、Redis、RabbitMQ）**：
```bash
# 適用於本地開發時不使用 Docker 運行前後端
docker-compose up -d postgres redis rabbitmq
```

**啟動特定服務（開發環境）**：
```bash
# 只啟動後端
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend

# 只啟動前端 Dashboard
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d dashboard

# 只啟動 LIFF
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d liff
```

### 4. 驗證服務狀態

```bash
# 查看所有容器狀態
docker-compose ps

# 查看特定服務日誌
docker-compose logs backend
docker-compose logs dashboard
docker-compose logs liff
```

## 🌐 服務存取端口

| 服務 | 端口 | URL | 說明 |
|------|------|-----|------|
| **Backend API** | 8000 | http://localhost:8000 | FastAPI 後端 |
| **Dashboard** | 3000 | http://localhost:3000 | Next.js 儀表板 |
| **LIFF** | 5173 | http://localhost:5173 | Vite + React LIFF App |
| **PostgreSQL** | 15432 | localhost:15432 | 資料庫 (外部連接) |
| **Redis** | 16379 | localhost:16379 | 快取服務 |
| **RabbitMQ Management** | 15672 | http://localhost:15672 | MQ 管理介面 |
| **MinIO Console** | 9001 | http://localhost:9001 | 物件儲存管理 |

## 🔧 常用指令

### 服務管理

```bash
# 啟動服務
docker-compose up -d [service_name]

# 停止服務
docker-compose stop [service_name]

# 重啟服務
docker-compose restart [service_name]

# 停止並移除所有容器
docker-compose down

# 停止並移除所有容器與 volumes
docker-compose down -v
```

### 日誌查看

```bash
# 查看所有服務日誌
docker-compose logs

# 持續追蹤日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f backend

# 查看最近 100 行日誌
docker-compose logs --tail=100
```

### 進入容器

```bash
# Backend
docker-compose exec backend bash

# Dashboard
docker-compose exec dashboard sh

# LIFF
docker-compose exec liff sh

# PostgreSQL
docker-compose exec postgres psql -U admin -d respirally_db
```

### 重新建置映像

```bash
# 重新建置所有服務
docker-compose build

# 重新建置特定服務
docker-compose build backend

# 強制重新建置（不使用快取）
docker-compose build --no-cache backend

# 重新建置並啟動
docker-compose up -d --build
```

## 🛠️ 開發模式

### Hot Reload 支援

所有服務都支援 hot reload，程式碼變更會自動重新載入：

- **Backend**: `uvicorn --reload` (FastAPI)
- **Dashboard**: `npm run dev` (Next.js Fast Refresh)
- **LIFF**: `npm run dev` (Vite HMR)

### Volume 掛載

開發模式下，本地目錄會掛載到容器：
```yaml
volumes:
  - ./backend:/app              # Backend 程式碼
  - ./frontend/dashboard:/app    # Dashboard 程式碼
  - ./frontend/liff:/app         # LIFF 程式碼
```

### 安裝新套件

**Backend (Python)**:
```bash
# 進入容器
docker-compose exec backend bash

# 使用 uv 安裝套件
uv add package-name

# 或直接從外部執行
docker-compose exec backend uv add package-name
```

**Frontend (Node.js)**:
```bash
# Dashboard
docker-compose exec dashboard npm install package-name

# LIFF
docker-compose exec liff npm install package-name
```

## 🐛 故障排除

### 1. 端口衝突

如果端口被占用：
```bash
# 檢查端口使用
lsof -i :8000
lsof -i :3000
lsof -i :5173

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 使用其他端口
```

### 2. 資料庫連接失敗

```bash
# 檢查 PostgreSQL 健康狀態
docker-compose ps postgres

# 查看 PostgreSQL 日誌
docker-compose logs postgres

# 手動測試連接
docker-compose exec postgres psql -U admin -d respirally_db -c "SELECT 1;"
```

### 3. Frontend 建置失敗

```bash
# 清除 node_modules cache
docker-compose down
docker volume rm respirally_dashboard_node_modules
docker volume rm respirally_liff_node_modules

# 重新建置
docker-compose up -d --build dashboard liff
```

### 4. Backend 依賴問題

```bash
# 清除 uv cache
docker-compose down
docker volume rm respirally_backend_cache

# 重新安裝依賴
docker-compose up -d --build backend
```

### 5. 查看容器資源使用

```bash
# 查看所有容器資源使用
docker stats

# 查看特定容器
docker stats respirally-backend
```

## 📊 健康檢查

所有服務都配置了健康檢查：

```bash
# 查看健康狀態
docker-compose ps

# Backend
curl http://localhost:8000/health

# Dashboard (需實作 /api/health 端點)
curl http://localhost:3000/api/health

# LIFF
curl http://localhost:5173/
```

## 🔒 生產環境部署

### 1. 使用生產配置

創建 `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      target: runner  # 使用生產階段
    environment:
      - ENVIRONMENT=production
    command: uvicorn src.respira_ally.main:app --host 0.0.0.0 --port 8000 --workers 4

  dashboard:
    build:
      target: runner
    environment:
      - NODE_ENV=production

  liff:
    build:
      target: runner
    environment:
      - NODE_ENV=production
```

啟動生產環境：
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. 環境變數管理

生產環境使用 `.env.production`:
```bash
cp .env .env.production
# 編輯 .env.production 設定生產環境變數

docker-compose --env-file .env.production up -d
```

### 3. 備份與還原

**備份資料庫**:
```bash
docker-compose exec postgres pg_dump -U admin respirally_db > backup.sql
```

**還原資料庫**:
```bash
cat backup.sql | docker-compose exec -T postgres psql -U admin -d respirally_db
```

## 🔄 更新與維護

### 更新服務

```bash
# 1. 拉取最新程式碼
git pull

# 2. 重新建置映像
docker-compose build

# 3. 停止舊容器
docker-compose down

# 4. 啟動新容器
docker-compose up -d

# 5. 驗證服務
docker-compose ps
```

### 清理未使用資源

```bash
# 清理停止的容器
docker container prune

# 清理未使用的映像
docker image prune

# 清理未使用的 volumes
docker volume prune

# 清理所有未使用資源（謹慎使用）
docker system prune -a
```

## 📝 開發最佳實踐

1. **使用 Docker Compose** - 統一開發環境
2. **定期備份資料** - 重要資料定期備份
3. **監控日誌** - 定期檢查容器日誌
4. **資源限制** - 生產環境設定資源限制
5. **安全更新** - 定期更新基礎映像

## 🆘 取得協助

如有問題，請：
1. 檢查 [故障排除](#-故障排除) 章節
2. 查看容器日誌：`docker-compose logs -f [service]`
3. 提交 Issue 到 GitHub 專案

---

**版本**: 2.0.0
**更新日期**: 2025-10-28
