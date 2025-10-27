# 綜合品質檢查清單 (Unified Quality Checklist) - RespiraAlly V2.0

---

**文件版本 (Document Version):** `v1.0.0`
**最後更新 (Last Updated):** `2025-10-23`
**主要作者 (Lead Author):** `TaskMaster Hub / Claude Code AI - Security Architect`
**狀態 (Status):** `使用中 (In Use)`

**審查對象 (Review Target):** `RespiraAlly V2.0 - AI-powered COPD Patient Management Platform`
**審查日期 (Review Date):** `2025-10-23`
**審查人員 (Reviewers):** `Security Architect, Privacy Consultant, Backend Lead, Frontend Lead`

**相關文檔 (Related Documents):**
- **系統架構:** [05_architecture_and_design.md](./05_architecture_and_design.md) - Clean Architecture 設計
- **API 設計規範:** [06_api_design_specification.md](./06_api_design_specification.md) - API 契約與安全
- **資料庫設計:** [database/schema_design_v1.0.md](./database/schema_design_v1.0.md) - 資料庫結構
- **前端架構:** [12_frontend_architecture_specification.md](./12_frontend_architecture_specification.md) - 前端安全規範

---

## 目錄 (Table of Contents)

- [A. 核心安全原則 (Core Security Principles)](#a-核心安全原則-core-security-principles)
- [B. 數據生命週期安全與隱私 (Data Lifecycle Security & Privacy)](#b-數據生命週期安全與隱私-data-lifecycle-security--privacy)
- [C. 應用程式安全 (Application Security)](#c-應用程式安全-application-security)
- [D. 基礎設施與運維安全 (Infrastructure & Operations Security)](#d-基礎設施與運維安全-infrastructure--operations-security)
- [E. 合規性 (Compliance)](#e-合規性-compliance)
- [F. 審查結論與行動項 (Review Conclusion & Action Items)](#f-審查結論與行動項-review-conclusion--action-items)
- [G. 生產準備就緒 (Production Readiness)](#g-生產準備就緒-production-readiness)

---

## 目的 (Purpose)

本檢查清單旨在提供一個統一的框架，用於在專案的關鍵階段（設計審查、Sprint Review、上線前）進行全面的**安全、隱私和生產準備就緒評估**。

**適用階段**:
- ✅ Sprint 0-1: 設計審查
- ✅ Sprint 2-5: 每週安全檢查
- ✅ Sprint 6: 上線前全面審查
- ✅ Phase 2+: 季度安全審計

---

## A. 核心安全原則 (Core Security Principles)

### A.1 基礎原則驗證

- [ ] **最小權限 (Least Privilege)**
  - [ ] 資料庫使用者權限：應用程式帳戶僅有 SELECT/INSERT/UPDATE 權限，無 DROP/ALTER 權限
  - [ ] API 端點權限：`@Depends(get_current_therapist)` 明確限制治療師專用端點
  - [ ] LINE LIFF 權限：僅請求必要的 LINE Profile 資料（user_id, display_name）
  - [ ] 病患僅可存取自己的資料（`patient_id == current_user.user_id`）

- [ ] **縱深防禦 (Defense in Depth)**
  - [ ] 多層安全控制：網路防火牆 + 應用程式防火牆 + API 認證 + 物件級授權
  - [ ] JWT 驗證 + Token 撤銷機制（Redis Blacklist）
  - [ ] HTTPS (TLS 1.3) + HSTS Header
  - [ ] 輸入驗證 (Pydantic) + 輸出編碼 + CSP Header

- [ ] **預設安全 (Secure by Default)**
  - [ ] FastAPI CORS 預設僅允許白名單域名
  - [ ] Database 連線字串使用環境變數 (`DATABASE_URL`)
  - [ ] Session Cookie 預設 `HttpOnly`, `Secure`, `SameSite=Strict`
  - [ ] 新建病患預設 `is_active=True`, `risk_level=LOW`

- [ ] **攻擊面最小化 (Minimize Attack Surface)**
  - [ ] 關閉不必要的 API 端點（`/docs` 僅在開發環境）
  - [ ] 禁用 FastAPI 預設的 `/redoc` 路由（生產環境）
  - [ ] 防火牆僅開放必要端口（443 HTTPS, 不開放 5432 PostgreSQL 外網）
  - [ ] Docker 容器以非 root 用戶運行

- [ ] **職責分離 (Separation of Duties)**
  - [ ] 關鍵操作需要治療師審核（病患風險等級變更）
  - [ ] 資料庫遷移需要 DBA 審核
  - [ ] 生產部署需要兩人批准（Backend Lead + DevOps）

---

## B. 數據生命週期安全與隱私 (Data Lifecycle Security & Privacy)

### B.1 數據分類與收集 (Data Classification & Collection)

- [ ] **數據分類 (Data Classification)**
  - [x] **公開資料**: 系統健康檢查端點 (`/health`)
  - [x] **內部資料**: 治療師統計報表
  - [x] **機密資料**: 病患健康記錄（DailyLog, Survey）
  - [x] **個人識別資訊 (PII)**: 病患姓名、LINE User ID、電話號碼
  - [x] **受保護健康資訊 (PHI)**: COPD 病程、用藥記錄、問卷結果

- [ ] **數據最小化 (Data Minimization)**
  - [ ] 僅收集必要資料：不收集病患地址、身份證字號（非必要）
  - [ ] LINE LIFF 僅請求 `openid` 與 `profile` Scope
  - [ ] 日誌系統不記錄 JWT Token、密碼、LINE User ID（僅記錄 `patient_id`）
  - [ ] API 響應僅返回必要欄位（不返回 `password_hash`）

- [ ] **用戶同意/告知 (User Consent/Notification)**
  - [ ] LINE LIFF 註冊前顯示隱私政策同意畫面
  - [ ] 明確告知資料用途（健康監測、風險預警）
  - [ ] 使用者可查看自己的資料（GET `/patients/{patient_id}`）
  - [ ] 使用者可要求刪除資料（GDPR Right to Erasure）

### B.2 數據傳輸 (Data in Transit)

- [ ] **傳輸加密 (Encryption in Transit)**
  - [ ] 所有外部通訊使用 HTTPS (TLS 1.3)
  - [ ] LINE LIFF → Backend API: HTTPS
  - [ ] Dashboard → Backend API: HTTPS
  - [ ] 證書來自 Let's Encrypt 或受信任的 CA

- [ ] **內部傳輸加密 (Internal Encryption)**
  - [ ] FastAPI → PostgreSQL: SSL/TLS 連線 (`sslmode=require`)
  - [ ] FastAPI → Redis: TLS 連線（Redis 6.0+）
  - [ ] FastAPI → RabbitMQ: AMQPS 協定

- [ ] **證書管理 (Certificate Management)**
  - [ ] TLS 證書有效期 > 30 天
  - [ ] 使用 Certbot 自動更新 Let's Encrypt 證書
  - [ ] 證書到期前 7 天自動告警

### B.3 數據儲存 (Data at Rest)

- [ ] **儲存加密 (Encryption at Rest)**
  - [ ] PostgreSQL 資料庫使用磁碟加密（AWS RDS: Encryption at Rest）
  - [ ] MinIO 檔案儲存使用 AES-256 加密
  - [ ] Redis 記憶體快照使用加密（RDB Persistence）

- [ ] **金鑰管理 (Key Management)**
  - [ ] JWT Secret 使用 AWS Secrets Manager 或 HashiCorp Vault
  - [ ] 資料庫密碼使用 Secrets Manager（不在 `.env` 文件）
  - [ ] MinIO Access Key 定期輪換（每 90 天）
  - [ ] 金鑰長度 ≥ 256 bits (JWT Secret)

- [ ] **數據備份安全**
  - [ ] PostgreSQL 自動每日備份（AWS RDS Automated Backups）
  - [ ] 備份資料使用相同等級加密 (AES-256)
  - [ ] 備份資料訪問需要額外授權（僅 DBA 可存取）

### B.4 數據使用與處理 (Data Usage & Processing)

- [ ] **日誌記錄中的敏感資訊**
  - [ ] 不記錄密碼、JWT Token、LINE User ID
  - [ ] 若必須記錄 `patient_id`，使用 UUID 而非姓名
  - [ ] 錯誤日誌遮罩敏感欄位：
    ```python
    # ✅ 正確
    logger.error(f"Patient {patient_id} login failed")
    # ❌ 錯誤
    logger.error(f"Patient {patient.name} login failed with password {password}")
    ```

- [ ] **第三方共享**
  - [ ] LINE Platform: 僅傳送通知訊息，不傳送健康資料
  - [ ] 無其他第三方資料共享
  - [ ] 若未來需共享，需簽訂資料處理協議 (DPA)

### B.5 數據保留與銷毀 (Data Retention & Disposal)

- [ ] **保留策略 (Retention Policy)**
  - [ ] 日誌資料 (DailyLog): 永久保留（醫療記錄需求）
  - [ ] 問卷資料 (Survey): 永久保留
  - [ ] 登入日誌 (LoginAttempt): 保留 90 天
  - [ ] 系統日誌 (Application Logs): 保留 30 天

- [ ] **安全銷毀 (Secure Disposal)**
  - [ ] 病患停用後，資料標記為 `is_active=False` 而非刪除
  - [ ] 若病患要求刪除（GDPR），使用 `TRUNCATE` 而非 `DELETE`
  - [ ] 刪除後的資料不可恢復（覆寫 7 次）

---

## C. 應用程式安全 (Application Security)

### C.1 身份驗證 (Authentication)

- [ ] **密碼策略**
  - [ ] 治療師密碼長度 ≥ 12 字元
  - [ ] 密碼複雜度要求：大小寫 + 數字 + 特殊符號
  - [ ] 支援 Google Authenticator MFA（未來功能）

- [ ] **憑證儲存**
  - [ ] 使用 `passlib` + `bcrypt` 雜湊（Cost Factor ≥ 12）
  - [ ] 密碼加鹽 (Salt) 自動生成
  - [ ] 絕不明文存儲密碼

- [ ] **會話管理 (Session Management)**
  - [ ] JWT Access Token 有效期 8 小時
  - [ ] JWT Refresh Token 有效期 30 天
  - [ ] Token 包含 `exp`, `iat`, `user_id`, `role`
  - [ ] Cookie 設定 `HttpOnly`, `Secure`, `SameSite=Strict`
  - [ ] 登出時將 Token 加入 Redis Blacklist

- [ ] **暴力破解防護**
  - [ ] 登入失敗 3 次鎖定帳戶 5 分鐘（使用 Redis 計數器）
  - [ ] 登入失敗 5 次鎖定帳戶 15 分鐘
  - [ ] 登入失敗 10 次鎖定帳戶 1 小時
  - [ ] API 速率限制：每 IP 每分鐘最多 60 次請求

### C.2 授權與訪問控制 (Authorization & Access Control)

- [ ] **物件級別授權 (Object-Level Authorization)**
  - [ ] 病患僅可存取自己的 DailyLog (`log.patient_id == current_user.user_id`)
  - [ ] 治療師僅可存取自己負責的病患 (`patient.therapist_id == current_user.user_id`)
  - [ ] 管理員可存取所有資料 (`current_user.role == UserRole.ADMIN`)

- [ ] **功能級別授權 (Function-Level Authorization)**
  - [ ] POST `/daily-logs`: 僅病患可提交
  - [ ] GET `/patients`: 僅治療師可查詢
  - [ ] DELETE `/patients/{id}`: 僅管理員可刪除
  - [ ] 使用 FastAPI `Depends(get_current_therapist)` 明確檢查

### C.3 輸入驗證與輸出編碼 (Input Validation & Output Encoding)

- [ ] **防止注入攻擊**
  - [ ] 使用 SQLAlchemy ORM 防止 SQL Injection
  - [ ] 所有資料庫查詢使用參數化查詢
  - [ ] 不使用字串拼接 SQL

- [ ] **防止跨站腳本 (XSS)**
  - [ ] Next.js 自動編碼輸出（React `{}` 語法）
  - [ ] 使用 Content Security Policy (CSP) Header:
    ```
    Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://static.line-scdn.net
    ```

- [ ] **防止跨站請求偽造 (CSRF)**
  - [ ] 使用 `SameSite=Strict` Cookie
  - [ ] API 使用 JWT (Stateless)，無 CSRF 風險
  - [ ] LIFF 使用 LINE LIFF SDK 內建 CSRF 保護

### C.4 API 安全 (API Security)

- [ ] **API 認證/授權**
  - [ ] 所有 API 端點（除 `/health`）需要 JWT 驗證
  - [ ] 使用 FastAPI `Depends(get_current_user)` 統一檢查
  - [ ] 無效 Token 返回 `401 Unauthorized`
  - [ ] 權限不足返回 `403 Forbidden`

- [ ] **速率限制**
  - [ ] 使用 `slowapi` 或 `fastapi-limiter` 限制請求速率
  - [ ] 一般端點: 60 req/min per IP
  - [ ] 登入端點: 5 req/min per IP
  - [ ] 語音上傳: 10 req/min per user

- [ ] **參數校驗**
  - [ ] 使用 Pydantic Schema 驗證所有輸入
  - [ ] 範例:
    ```python
    class DailyLogCreate(BaseModel):
        water_ml: int = Field(..., ge=0, le=4000)  # 0-4000ml
        cough_level: int = Field(..., ge=0, le=10)  # 0-10
    ```

- [ ] **避免數據過度暴露**
  - [ ] 使用 Pydantic Response Model 明確定義返回欄位
  - [ ] 不返回 `password_hash`, `jwt_secret`
  - [ ] 範例:
    ```python
    class PatientResponse(BaseModel):
        patient_id: UUID
        full_name: str
        # 不包含 password_hash

        class Config:
            from_attributes = True
    ```

### C.5 依賴庫安全 (Dependency Security)

- [ ] **漏洞掃描**
  - [ ] 使用 `pip-audit` 或 `safety` 定期掃描 Python 依賴
  - [ ] 使用 `npm audit` 掃描 JavaScript 依賴
  - [ ] CI/CD 整合自動掃描（每次 PR）

- [ ] **更新策略**
  - [ ] 高危漏洞 (CVSS ≥ 7.0) 立即更新
  - [ ] 中危漏洞 (CVSS 4.0-6.9) 7 天內更新
  - [ ] 低危漏洞 (CVSS < 4.0) 下個 Sprint 更新

---

## D. 基礎設施與運維安全 (Infrastructure & Operations Security)

### D.1 網路安全 (Network Security)

- [ ] **防火牆/安全組**
  - [ ] 僅開放 443 (HTTPS), 80 (HTTP redirect to HTTPS)
  - [ ] 資料庫端口 5432 僅允許應用程式 Security Group
  - [ ] Redis 端口 6379 僅允許應用程式 Security Group
  - [ ] RabbitMQ 端口 5672 僅允許應用程式 Security Group

- [ ] **DDoS 防護**
  - [ ] 使用 Cloudflare 或 AWS Shield Standard
  - [ ] 設定流量閾值告警（> 10,000 req/min）

### D.2 機密管理 (Secrets Management)

- [ ] **安全儲存**
  - [ ] 使用 AWS Secrets Manager 或 HashiCorp Vault
  - [ ] 環境變數通過 `.env` 文件（本地開發）或 AWS Systems Manager Parameter Store（生產）
  - [ ] 絕不在 Git 提交機密資訊（`.env` 已加入 `.gitignore`）

- [ ] **權限與輪換**
  - [ ] 機密訪問需要 IAM 角色授權
  - [ ] JWT Secret 每 90 天輪換
  - [ ] 資料庫密碼每 180 天輪換

### D.3 Docker/容器安全 (Container Security)

- [ ] **最小化基礎鏡像**
  - [ ] 使用官方 Python Slim 鏡像（`python:3.11-slim`）
  - [ ] 使用官方 Node Alpine 鏡像（`node:18-alpine`）
  - [ ] 避免使用 `latest` 標籤，明確指定版本

- [ ] **非 Root 用戶運行**
  - [ ] Dockerfile 創建非 root 用戶：
    ```dockerfile
    RUN useradd -m -u 1000 appuser
    USER appuser
    ```

- [ ] **鏡像掃描**
  - [ ] CI/CD 使用 Trivy 或 Snyk 掃描容器鏡像
  - [ ] 高危漏洞阻止部署

### D.4 日誌與監控 (Logging & Monitoring)

- [ ] **安全事件日誌**
  - [ ] 記錄所有登入嘗試（成功/失敗）
  - [ ] 記錄權限變更（治療師新增病患、管理員刪除帳戶）
  - [ ] 記錄 API 403/401 錯誤（潛在攻擊）

- [ ] **安全告警**
  - [ ] 登入失敗超過 10 次/分鐘告警
  - [ ] 資料庫連線失敗告警
  - [ ] API 500 錯誤率超過 1% 告警

---

## E. 合規性 (Compliance)

### E.1 法規識別

- [ ] **台灣個人資料保護法 (PDPA)**
  - [ ] 告知使用者資料收集目的與範圍
  - [ ] 取得使用者明確同意
  - [ ] 提供使用者查詢、修改、刪除資料的機制

- [ ] **HIPAA (Health Insurance Portability and Accountability Act)** (若適用)
  - [ ] 加密傳輸與儲存健康資訊
  - [ ] 稽核追蹤（誰存取了哪些病患資料）
  - [ ] 資料備份與災難恢復計畫

- [ ] **GDPR (General Data Protection Regulation)** (若適用)
  - [ ] Right to Access: 使用者可查詢自己的資料
  - [ ] Right to Erasure: 使用者可要求刪除資料
  - [ ] Data Portability: 使用者可匯出資料 (JSON 格式)

### E.2 合規性措施

- [ ] **資料處理協議 (DPA)**
  - [ ] 與 LINE Platform 簽訂 DPA（若傳輸 PII）
  - [ ] 與雲端服務商簽訂 BAA (HIPAA 需求)

- [ ] **隱私政策 (Privacy Policy)**
  - [ ] 明確說明資料收集、使用、共享、保留政策
  - [ ] 公開於 LIFF 註冊頁面與 Dashboard

- [ ] **稽核追蹤 (Audit Trail)**
  - [ ] 記錄所有資料存取（誰、何時、存取哪些病患資料）
  - [ ] 保留稽核日誌 90 天
  - [ ] 可匯出稽核日誌供監管機構審查

---

## F. 審查結論與行動項 (Review Conclusion & Action Items)

### 主要風險 (Key Risks Identified)

| # | 風險描述 | 嚴重性 | 影響 | 當前狀態 |
|:-:|:---------|:------:|:-----|:---------|
| 1 | JWT Secret 存儲在 `.env` 文件 | 🔴 高 | 若洩漏可偽造任何使用者 Token | ⏳ Sprint 2 移至 Secrets Manager |
| 2 | 缺少 API 速率限制 | 🟡 中 | 可能遭受 DDoS 攻擊 | ⏳ Sprint 3 實作 slowapi |
| 3 | 未實作 MFA (多因子認證) | 🟡 中 | 治療師帳戶易遭破解 | 📋 Phase 2 功能 |
| 4 | 缺少容器鏡像掃描 | 🟡 中 | 可能部署有漏洞的鏡像 | ⏳ Sprint 4 整合 Trivy |
| 5 | 未實作稽核追蹤 | 🟢 低 | 無法追溯資料存取歷史 | 📋 Phase 2 功能 |

### 行動項 (Action Items)

| # | 行動項描述 | 負責人 | 預計完成日期 | 優先級 | 狀態 |
|:-:|:-----------|:-------|:-------------|:------:|:-----|
| 1 | 將 JWT Secret 移至 AWS Secrets Manager | Backend Lead | 2025-11-07 | P0 | 待辦 |
| 2 | 實作 API 速率限制 (slowapi) | Backend Lead | 2025-11-14 | P1 | 待辦 |
| 3 | 整合 Trivy 容器掃描到 CI/CD | DevOps | 2025-11-21 | P1 | 待辦 |
| 4 | 撰寫隱私政策並整合到 LIFF | Frontend Lead | 2025-11-07 | P0 | 待辦 |
| 5 | 設定 Content Security Policy (CSP) Header | Frontend Lead | 2025-11-14 | P1 | 待辦 |
| 6 | 實作登入失敗鎖定機制 | Backend Lead | 2025-10-28 | P0 | ✅ 已完成 |

### 整體評估 (Overall Assessment)

**安全成熟度**: 🟡 **中等**

**評語**:
- ✅ **已達成**: 基礎認證授權、HTTPS 傳輸加密、ORM 防 SQL Injection
- ⚠️ **需改善**: 機密管理、API 速率限制、容器安全掃描
- 📋 **未來計畫**: MFA、稽核追蹤、資料匯出功能

**建議**:
- **Sprint 2-3**: 完成 P0/P1 行動項後，可進入 Beta 測試
- **Sprint 4-5**: 完成 P2 行動項後，可正式上線
- **Phase 2**: 實作進階安全功能（MFA、稽核追蹤）

---

## G. 生產準備就緒 (Production Readiness)

*此部分確保系統在上線前，在可觀測性、可靠性、可擴展性和可維護性等方面已達到生產標準。*

### G.1 可觀測性 (Observability)

- [ ] **監控儀表板 (Monitoring Dashboard)**
  - [ ] 使用 Grafana 建立核心指標儀表板
  - [ ] 監控指標：CPU、Memory、Disk I/O、Network
  - [ ] 應用程式指標：API 請求數、錯誤率、延遲

- [ ] **核心指標 (Key Metrics - SLIs)**
  - [ ] **Latency (延遲)**: API P95 < 500ms, P99 < 1000ms
  - [ ] **Traffic (流量)**: 支援 1000 req/min (初期)
  - [ ] **Errors (錯誤率)**: < 1% (5xx 錯誤)
  - [ ] **Saturation (飽和度)**: CPU < 70%, Memory < 80%

- [ ] **日誌 (Logging)**
  - [ ] 使用結構化日誌 (JSON 格式)
    ```python
    logger.info("Daily log submitted", extra={
        "patient_id": str(patient_id),
        "log_id": str(log_id),
        "log_date": log_date.isoformat()
    })
    ```
  - [ ] 日誌集中管理（Loki + Grafana 或 ELK Stack）
  - [ ] 日誌級別可在運行時調整（DEBUG/INFO/WARNING/ERROR）

- [ ] **全鏈路追蹤 (Distributed Tracing)**
  - [ ] 使用 OpenTelemetry 整合
  - [ ] 追蹤 API → Service → Repository → Database 完整鏈路
  - [ ] Jaeger UI 可視化追蹤

- [ ] **告警 (Alerting)**
  - [ ] 錯誤率 > 5% 告警（Slack/Email）
  - [ ] API 延遲 P95 > 1000ms 告警
  - [ ] 資料庫連線池耗盡告警
  - [ ] 磁碟空間 < 20% 告警

### G.2 可靠性與彈性 (Reliability & Resilience)

- [ ] **健康檢查 (Health Checks)**
  - [ ] 實作 `/health` 端點（無需認證）
    ```python
    @router.get("/health")
    async def health_check(db: AsyncSession = Depends(get_db)):
        # 檢查資料庫連線
        await db.execute(text("SELECT 1"))
        # 檢查 Redis 連線
        await redis_client.ping()
        return {"status": "ok", "timestamp": datetime.utcnow()}
    ```
  - [ ] Kubernetes Liveness Probe: GET `/health`
  - [ ] Kubernetes Readiness Probe: GET `/health`

- [ ] **優雅啟停 (Graceful Shutdown)**
  - [ ] FastAPI 處理 `SIGTERM` 信號
  - [ ] 完成進行中的請求（最多等待 30 秒）
  - [ ] 關閉資料庫連線池
  - [ ] 關閉 RabbitMQ 連線

- [ ] **重試與超時 (Retries & Timeouts)**
  - [ ] 外部 API 調用設定超時（5 秒）
  - [ ] 資料庫查詢超時（10 秒）
  - [ ] RabbitMQ 消費者重試機制（最多 3 次，指數退避）

- [ ] **故障轉移 (Failover)**
  - [ ] PostgreSQL 主從複製（AWS RDS Multi-AZ）
  - [ ] Redis Sentinel 高可用配置
  - [ ] RabbitMQ 叢集模式（3 節點）

- [ ] **備份與恢復 (Backup & Recovery)**
  - [ ] PostgreSQL 每日自動備份（AWS RDS）
  - [ ] 備份保留 30 天
  - [ ] 每季度進行災難恢復演練（Disaster Recovery Drill）

### G.3 性能與可擴展性 (Performance & Scalability)

- [ ] **負載測試 (Load Testing)**
  - [ ] 使用 Locust 或 k6 進行負載測試
  - [ ] 測試目標：1000 concurrent users, 10,000 req/min
  - [ ] 驗證 API 延遲 P95 < 500ms

- [ ] **容量規劃 (Capacity Planning)**
  - [ ] 初期支援 100 位治療師、1000 位病患
  - [ ] 每位病患每日 1 筆日誌 → 30,000 筆/月
  - [ ] 資料庫容量：100 GB（2 年資料）
  - [ ] Redis 容量：4 GB (快取 + Session)

- [ ] **水平擴展 (Horizontal Scaling)**
  - [ ] FastAPI 無狀態設計（Session 存 Redis）
  - [ ] Kubernetes HPA (Horizontal Pod Autoscaler):
    - CPU > 70% → 自動增加 Pod
    - CPU < 30% → 自動減少 Pod
  - [ ] 最小 Pod 數: 2, 最大 Pod 數: 10

- [ ] **依賴擴展性**
  - [ ] PostgreSQL 支援讀寫分離（Master/Slave）
  - [ ] Redis 支援分片（Redis Cluster）
  - [ ] RabbitMQ 支援叢集擴展

### G.4 可維護性與文檔 (Maintainability & Documentation)

- [ ] **部署文檔/腳本 (Runbook/Playbook)**
  - [ ] 部署步驟文檔（`docs/deployment/deploy.md`）
  - [ ] 回滾步驟文檔（`docs/deployment/rollback.md`）
  - [ ] 常見問題排查（`docs/troubleshooting.md`）

- [ ] **CI/CD**
  - [ ] GitHub Actions 自動測試（每次 PR）
  - [ ] 自動部署到 Staging（main 分支）
  - [ ] 手動批准部署到 Production

- [ ] **配置管理 (Configuration Management)**
  - [ ] 使用 ConfigMap (Kubernetes) 或環境變數
  - [ ] 不硬編碼配置在代碼中
  - [ ] 配置變更需要 Code Review

- [ ] **功能開關 (Feature Flags)**
  - [ ] 使用 LaunchDarkly 或自建 Feature Flag 系統
  - [ ] 重大功能使用 Feature Flag（可快速禁用）
  - [ ] 範例：`ENABLE_MFA=false` → 上線後漸進啟用

---

## 簽署 (Sign-off)

**安全審查團隊代表:** _______________
**日期:** _______________

**專案負責人 (Backend Lead):** _______________
**日期:** _______________

**DevOps/SRE Lead:** _______________
**日期:** _______________

---

## 附錄：檢查清單快速摘要

### 上線前必須完成 (P0)

- [ ] JWT Secret 移至 Secrets Manager
- [ ] 實作登入失敗鎖定機制（已完成）
- [ ] 實作 `/health` 健康檢查端點
- [ ] 設定 HTTPS (TLS 1.3)
- [ ] 設定 CORS 白名單
- [ ] 密碼使用 bcrypt 雜湊
- [ ] 資料庫使用 SSL/TLS 連線
- [ ] 撰寫隱私政策並整合到 LIFF

### 上線後 30 天內完成 (P1)

- [ ] 實作 API 速率限制
- [ ] 整合容器鏡像掃描（Trivy）
- [ ] 設定 Grafana 監控儀表板
- [ ] 設定告警（錯誤率、延遲）
- [ ] 進行負載測試
- [ ] 撰寫災難恢復演練文檔

### Phase 2 功能 (P2)

- [ ] 實作 MFA (多因子認證)
- [ ] 實作稽核追蹤（Audit Trail）
- [ ] 實作資料匯出功能 (GDPR)
- [ ] 實作全鏈路追蹤（OpenTelemetry）

---

**最後審查**: 2025-10-23 by TaskMaster Hub
**下次審查**: Sprint 3 Week 1 (2025-11-07) - 驗證 P0 行動項完成狀態
