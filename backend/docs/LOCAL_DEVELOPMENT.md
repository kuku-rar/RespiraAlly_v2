# RespiraAlly V2.0 - 本地開發指南

**最後更新**: 2025-10-20
**狀態**: ✅ 基礎設施就緒 | ⚠️ Auth API 有已知問題

---

## 🚀 快速啟動（5 分鐘）

### 前置需求
- Docker & Docker Compose
- Python 3.11+ (透過 uv 管理)
- Git

### 一鍵啟動

```bash
# 1. 啟動基礎設施（PostgreSQL + Redis + RabbitMQ）
docker-compose up -d postgres redis rabbitmq

# 2. 驗證所有服務健康
docker-compose ps
# 預期：3 個服務全部顯示 (healthy)

# 3. 啟動後端 API
cd backend
uv run uvicorn src.respira_ally.main:app --reload --host 0.0.0.0 --port 8000

# 4. 驗證 API
curl http://localhost:8000/health
# 預期：{"status":"healthy","version":"2.0.0","environment":"development"}
```

### 服務訪問端點

| 服務 | URL | 說明 |
|------|-----|------|
| 後端 API | http://localhost:8000 | FastAPI 主服務 |
| Swagger UI | http://localhost:8000/api/docs | API 文檔（互動式） |
| ReDoc | http://localhost:8000/api/redoc | API 文檔（閱讀模式） |
| PostgreSQL | localhost:15432 | 資料庫（避免 5432 衝突） |
| Redis | localhost:16379 | 快取（避免 6379 衝突） |
| RabbitMQ | localhost:5672 | 訊息佇列 |
| RabbitMQ UI | http://localhost:15672 | 管理介面（guest/guest） |

---

## 📦 基礎設施詳細說明

### PostgreSQL + pgvector
```yaml
Image: pgvector/pgvector:pg15
Port: 15432 (外部) → 5432 (容器內)
Database: respirally_db
User: admin / admin
Extensions: vector (v0.8.1), uuid-ossp (v1.1)
```

**驗證資料庫連接**:
```bash
docker exec -it respirally-postgres psql -U admin -d respirally_db -c "\dx"
# 預期顯示: vector | uuid-ossp
```

### Redis
```yaml
Image: redis:7-alpine
Port: 16379 (外部) → 6379 (容器內)
Persistence: AOF (appendonly yes)
```

**驗證 Redis 連接**:
```bash
docker exec respirally-redis redis-cli ping
# 預期: PONG
```

### RabbitMQ
```yaml
Image: rabbitmq:3-management-alpine
Port: 5672 (AMQP), 15672 (Management UI)
Credentials: guest / guest
```

**驗證 RabbitMQ**:
訪問 http://localhost:15672 使用 guest/guest 登入

---

## 🔧 開發流程

### 環境變數管理

**後端 (.env)**:
```bash
# 重要：Redis Port 已改為 16379 避免衝突
REDIS_PORT=16379

# PostgreSQL 使用 15432 避免衝突
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:15432/respirally_db

# 其他配置見 backend/.env.example
```

### 資料庫 Migration

```bash
# 查看當前版本
cd backend
uv run alembic current

# 生成新 migration
uv run alembic revision --autogenerate -m "description"

# 執行 migration
uv run alembic upgrade head

# 回滾
uv run alembic downgrade -1
```

### 執行測試

```bash
cd backend

# 執行所有測試
uv run pytest

# 執行特定測試
uv run pytest tests/test_auth.py -v

# 執行測試並產生覆蓋率報告
uv run pytest --cov=src --cov-report=html
```

---

## ⚠️ 已知問題與解決方案

### 問題 1: Auth API 註冊失敗 (bcrypt 兼容性)

**錯誤訊息**:
```
ValueError: password cannot be longer than 72 bytes
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**原因**: passlib 與新版 bcrypt (>4.0) 不兼容

**臨時解決方案**:
1. 使用短密碼（<72 bytes）
2. 或降級 bcrypt 版本：
   ```bash
   cd backend
   uv pip install 'bcrypt<4.0'
   ```

**永久解決方案** (待實作):
- 遷移到 `passlib[bcrypt]` 或直接使用 `bcrypt` 庫
- 追蹤 Issue: https://github.com/pyca/bcrypt/issues/684

### 問題 2: Port 衝突

**症狀**: Redis/PostgreSQL 無法啟動

**解決方案**:
- Redis 已改用 16379
- PostgreSQL 已改用 15432
- 確認 `.env` 中的 port 配置一致

### 問題 3: Docker Volume 權限問題 (WSL2)

**症狀**: 無法掛載 init-db.sql

**解決方案**:
```bash
# 手動執行初始化
docker exec -i respirally-postgres psql -U admin -d respirally_db < database/init-db.sql
```

---

## 🧪 驗證清單

啟動環境後，逐項驗證：

- [ ] PostgreSQL 容器健康 (`docker-compose ps` 顯示 healthy)
- [ ] Redis 容器健康
- [ ] RabbitMQ 容器健康
- [ ] 後端 API 啟動成功 (`/health` 回應 200)
- [ ] Swagger UI 可訪問 (`/api/docs`)
- [ ] 資料庫 pgvector 擴展已安裝
- [ ] Redis PING 回應 PONG
- [ ] RabbitMQ Management UI 可登入

---

## 🐛 除錯技巧

### 查看容器日誌
```bash
# PostgreSQL
docker logs respirally-postgres

# Redis
docker logs respirally-redis

# RabbitMQ
docker logs respirally-rabbitmq

# 後端 API（如果在容器中）
docker logs respirally-backend
```

### 進入容器 Shell
```bash
# PostgreSQL
docker exec -it respirally-postgres psql -U admin -d respirally_db

# Redis
docker exec -it respirally-redis redis-cli -p 6379

# RabbitMQ
docker exec -it respirally-rabbitmq rabbitmq-diagnostics status
```

### 重啟所有服務
```bash
docker-compose down
docker-compose up -d postgres redis rabbitmq
# 重新啟動後端 API
```

---

## 📊 效能監控

### 資料庫查詢分析
```sql
-- 查看慢查詢
SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- 查看資料庫大小
SELECT pg_size_pretty(pg_database_size('respirally_db'));
```

### Redis 監控
```bash
docker exec respirally-redis redis-cli INFO stats
```

### RabbitMQ 監控
訪問 http://localhost:15672/#/queues

---

## 🔄 常見操作

### 重置資料庫
```bash
# 刪除所有資料並重新 migrate
cd backend
uv run alembic downgrade base
uv run alembic upgrade head
```

### 清空 Redis 快取
```bash
docker exec respirally-redis redis-cli FLUSHALL
```

### 重建容器
```bash
docker-compose down -v  # -v 刪除 volumes
docker-compose up -d postgres redis rabbitmq
```

---

## 📞 取得協助

- **文檔**: 查看 `docs/` 目錄下的其他文件
- **API 文檔**: http://localhost:8000/api/docs
- **已知問題**: 參考本文件「已知問題」章節
- **Issue Tracker**: GitHub Issues

---

**維護者**: RespiraAlly Development Team
**授權**: MIT
