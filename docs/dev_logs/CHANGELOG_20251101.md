# RespiraAlly V2.0 - 開發變更日誌

**日期**: 2025-11-01
**衝刺 (Sprint)**: 4 - 技術債務償還 (TD-002)
**里程碑**: 資料庫架構優化與 Schema 建置

---

## 📋 總結

完成 TD-002 技術債務償還並建立完整的 development 和 production schema：

### ✅ 已完成任務

#### 1. **技術債務 TD-002: 移除 temp_line_id 設計缺陷** ✅
**Commits**: `7359fbb`, `5514aa2`, `20a3616`, `fd7a074`

**問題描述**:
- `temp_line_id` 欄位使用臨時值 (`temp_xxxx`) 污染永久的 `line_user_id` 欄位
- 違反 "Good Taste" 原則：應使用 NULL 表示「尚未綁定」狀態
- 增加資料一致性風險，造成特殊情況處理

**解決方案**:
根據 Linus Torvalds 的 "Good Taste" 哲學，使用 NULL 語義：
- NULL = 尚未綁定 LINE (Patient 可在未綁定前創建)
- 非 NULL = 已綁定 LINE User ID (永久值)
- 消除特殊情況，簡化邏輯

**實作任務**:

##### TD-002.1: Alembic Migration - 清理 temp_line_id ✅
**檔案**: `backend/alembic/versions/2025_11_01_0825-remove_temp_line_id_constraint.py`

```sql
-- Step 1: 清理現有的 temp_line_id 值
UPDATE users
SET line_user_id = NULL
WHERE line_user_id LIKE 'temp_%';

-- Step 2: 移除 users_patient_line_check 約束
DROP CONSTRAINT users_patient_line_check;

-- Step 3: 放寬 users_login_method_check 約束
-- 允許 PATIENT 在沒有登入方式的情況下存在
DROP CONSTRAINT users_login_method_check;
CREATE CONSTRAINT users_login_method_check
CHECK (role = 'PATIENT' OR (line_user_id IS NOT NULL OR email IS NOT NULL));
```

**修復歷程**:
- ❌ 初始 migration 依賴錯誤 (`down_revision = 'daa11447efa1'`)
- ⚠️ 遇到 Multiple head revisions 錯誤
- ✅ 修正為正確依賴 (`down_revision = 'add_supervisor_admin_roles'`)
- ✅ Migration 執行成功
- ✅ 手動修復資料庫約束確認正確性

##### TD-002.2: ORM Model 更新 ✅
**檔案**: `backend/src/respira_ally/infrastructure/database/models/user.py`

**變更前**:
```python
__table_args__ = (
    CheckConstraint(
        "line_user_id IS NOT NULL OR email IS NOT NULL",
        name="users_login_method_check",
    ),
    CheckConstraint(
        "role != 'PATIENT' OR line_user_id IS NOT NULL",
        name="users_patient_line_check"  # ← 需移除
    ),
    # ...
)
```

**變更後**:
```python
__table_args__ = (
    # Login method requirement (relaxed for PATIENT - TD-002)
    CheckConstraint(
        "role = 'PATIENT' OR (line_user_id IS NOT NULL OR email IS NOT NULL)",
        name="users_login_method_check",
    ),
    # THERAPIST must have email
    CheckConstraint(
        "role != 'THERAPIST' OR email IS NOT NULL",
        name="users_therapist_email_check"
    ),
    # Note: users_patient_line_check removed in TD-002
)
```

##### TD-002.3: API Router 重構 ✅
**檔案**: `backend/src/respira_ally/api/v1/routers/patient.py`

**變更前 (Line 75-83)**:
```python
import secrets
# ...
# 2. Create user account for patient
temp_line_id = f"temp_{secrets.token_hex(8)}"  # ← 移除
new_user = UserModel(
    line_user_id=temp_line_id,  # ← 使用臨時值
    role="PATIENT",
    email=None,
    hashed_password=None,
)
```

**變更後**:
```python
# 2. Create user account for patient (TD-002: line_user_id=NULL before LINE binding)
new_user = UserModel(
    line_user_id=None,  # NULL until LINE binding (fixed in TD-002)
    role="PATIENT",
    email=None,  # Patients don't have email (use LINE)
    hashed_password=None,  # No password for LINE users
)
```

##### TD-002.4: 文檔更新 ✅

**更新檔案**:
1. **API 設計規範** (`docs/06_api_design_specification.md`)
   - 版本: v1.0.0 → v1.1.0
   - 更新 `PatientCreate` schema，標註 `line_user_id` 為可選
   - 新增 TD-002 變更記錄說明

2. **資料庫 Schema 設計** (`docs/database/schema_design_v1.0.md`)
   - 版本: v2.1 → v2.2
   - 更新 `users` 表約束文檔
   - 移除 `users_patient_line_check` 約束說明
   - 更新 `users_login_method_check` 約束邏輯

3. **架構設計文檔** (`docs/05_architecture_and_design.md`)
   - 新增 ADR-010: TD-002 決策記錄
   - 新增 Appendix D: Technical Debt Fixes 章節
   - 記錄問題、根本原因、解決方案、影響

**測試驗證**:
- ✅ Migration 回滾測試通過
- ✅ 資料庫約束驗證通過
- ✅ API 端點測試通過
- ✅ 向後相容性驗證通過

---

#### 2. **Database Schema 建置: Development & Production** ✅
**Commit**: `162c2fb`

**業務需求**:
在確認 TD-002 成功實作後，建立完整的 development 和 production schema，確保兩個環境的資料庫結構一致。

**實作步驟**:

##### Phase 1: Production Schema 建立 ✅

**建立資料表結構**:
```sql
CREATE SCHEMA IF NOT EXISTS production;

-- 複製 6 個核心資料表 (不含資料)
CREATE TABLE production.users (LIKE public.users INCLUDING ALL);
CREATE TABLE production.patient_profiles (LIKE public.patient_profiles INCLUDING ALL);
CREATE TABLE production.therapist_profiles (LIKE public.therapist_profiles INCLUDING ALL);
CREATE TABLE production.daily_logs (LIKE public.daily_logs INCLUDING ALL);
CREATE TABLE production.event_logs (LIKE public.event_logs INCLUDING ALL);
CREATE TABLE production.survey_responses (LIKE public.survey_responses INCLUDING ALL);
```

**添加外鍵約束**:
```sql
-- 5 個外鍵約束 (對應 public schema)
ALTER TABLE production.daily_logs
ADD CONSTRAINT daily_logs_patient_id_fkey
FOREIGN KEY (patient_id) REFERENCES production.patient_profiles(user_id) ON DELETE CASCADE;

ALTER TABLE production.patient_profiles
ADD CONSTRAINT patient_profiles_therapist_id_fkey
FOREIGN KEY (therapist_id) REFERENCES production.therapist_profiles(user_id) ON DELETE SET NULL;

ALTER TABLE production.patient_profiles
ADD CONSTRAINT patient_profiles_user_id_fkey
FOREIGN KEY (user_id) REFERENCES production.users(user_id) ON DELETE CASCADE;

ALTER TABLE production.survey_responses
ADD CONSTRAINT survey_responses_patient_id_fkey
FOREIGN KEY (patient_id) REFERENCES production.patient_profiles(user_id) ON DELETE CASCADE;

ALTER TABLE production.therapist_profiles
ADD CONSTRAINT therapist_profiles_user_id_fkey
FOREIGN KEY (user_id) REFERENCES production.users(user_id) ON DELETE CASCADE;
```

##### Phase 2: Development Schema 完善 ✅

**建立資料表結構**:
```sql
-- Development schema 已有 copd_knowledge_base，補充核心 6 表
CREATE TABLE development.users (LIKE public.users INCLUDING ALL);
CREATE TABLE development.patient_profiles (LIKE public.patient_profiles INCLUDING ALL);
CREATE TABLE development.therapist_profiles (LIKE public.therapist_profiles INCLUDING ALL);
CREATE TABLE development.daily_logs (LIKE public.daily_logs INCLUDING ALL);
CREATE TABLE development.event_logs (LIKE public.event_logs INCLUDING ALL);
CREATE TABLE development.survey_responses (LIKE public.survey_responses INCLUDING ALL);
```

**添加外鍵約束** (與 production 相同):
```sql
-- 5 個外鍵約束
ALTER TABLE development.daily_logs
ADD CONSTRAINT daily_logs_patient_id_fkey
FOREIGN KEY (patient_id) REFERENCES development.patient_profiles(user_id) ON DELETE CASCADE;

ALTER TABLE development.patient_profiles
ADD CONSTRAINT patient_profiles_therapist_id_fkey
FOREIGN KEY (therapist_id) REFERENCES development.therapist_profiles(user_id) ON DELETE SET NULL;

ALTER TABLE development.patient_profiles
ADD CONSTRAINT patient_profiles_user_id_fkey
FOREIGN KEY (user_id) REFERENCES development.users(user_id) ON DELETE CASCADE;

ALTER TABLE development.survey_responses
ADD CONSTRAINT survey_responses_patient_id_fkey
FOREIGN KEY (patient_id) REFERENCES development.patient_profiles(user_id) ON DELETE CASCADE;

ALTER TABLE development.therapist_profiles
ADD CONSTRAINT therapist_profiles_user_id_fkey
FOREIGN KEY (user_id) REFERENCES development.users(user_id) ON DELETE CASCADE;
```

##### Phase 3: Docker 容器重啟驗證 ✅

**重啟流程**:
```bash
docker restart respirally-postgres
# 等待容器啟動 (健康檢查)
# ✅ 容器狀態: healthy (22 seconds)
```

**驗證檢查**:
```sql
-- 1. Schema 與資料表確認
SELECT table_schema, COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema IN ('public', 'development', 'production', 'test_data')
GROUP BY table_schema;

-- 結果:
-- public: 6 表
-- development: 7 表 (含 copd_knowledge_base)
-- production: 6 表
-- test_data: 6 表

-- 2. 約束數量確認
SELECT nsp.nspname as schema_name,
       COUNT(*) FILTER (WHERE con.contype = 'p') as pk,
       COUNT(*) FILTER (WHERE con.contype = 'f') as fk,
       COUNT(*) FILTER (WHERE con.contype = 'u') as unique,
       COUNT(*) FILTER (WHERE con.contype = 'c') as check,
       COUNT(*) as total
FROM pg_namespace nsp
LEFT JOIN pg_constraint con ON con.connamespace = nsp.oid
WHERE nsp.nspname IN ('public', 'development', 'production')
GROUP BY nsp.nspname;

-- 結果:
-- public: 6 PK + 5 FK + 4 Unique + 12 Check = 27 Total
-- development: 7 PK + 5 FK + 4 Unique + 12 Check = 28 Total
-- production: 6 PK + 5 FK + 4 Unique + 12 Check = 27 Total
```

**資料筆數驗證**:
- ✅ public.users: 1 筆 (測試資料)
- ✅ development 所有表: 0 筆 (空表)
- ✅ production 所有表: 0 筆 (空表)

##### Phase 4: 文檔更新 ✅

**新建文檔**: `docs/database/database_status_2025_11_01.md`

包含內容:
- 📊 Schema 總覽 (4 個 schema 的統計)
- 📁 資料表分布詳情
- 🔗 外鍵約束狀態 (完整列表)
- 📈 資料筆數統計
- ✅ 關鍵發現與建議
- 📜 更新記錄 (包含執行指令與驗證結果)

---

## 📊 最終資料庫狀態

### Schema 結構對比

| Schema | 資料表數量 | 主鍵 | 外鍵 | 唯一約束 | 檢查約束 | 總約束數 |
|--------|-----------|------|------|---------|---------|---------|
| **public** | 6 | 6 | 5 | 4 | 12 | 27 |
| **development** | 7 | 7 | 5 | 4 | 12 | 28 |
| **production** | 6 | 6 | 5 | 4 | 12 | 27 |
| **test_data** | 6 | 6 | 5 | 4 | 9 | 24 |

### 外鍵約束 (Development & Production)

兩個 schema 具有相同的 5 個外鍵約束:

1. `daily_logs.patient_id` → `patient_profiles.user_id` (CASCADE)
2. `patient_profiles.therapist_id` → `therapist_profiles.user_id` (SET NULL)
3. `patient_profiles.user_id` → `users.user_id` (CASCADE)
4. `survey_responses.patient_id` → `patient_profiles.user_id` (CASCADE)
5. `therapist_profiles.user_id` → `users.user_id` (CASCADE)

### 資料完整性保護

- ✅ Development schema: 完整的參照完整性約束
- ✅ Production schema: 完整的參照完整性約束
- ✅ Docker 重啟驗證: 所有設定持久化
- ✅ 所有表為空: 符合初始建置要求

---

## 🎯 技術債務狀態更新

### TD-002: 移除 temp_line_id 設計缺陷

**狀態**: ✅ 完成
**優先級**: P0
**預估工時**: 8h
**實際工時**: 約 8h
**完成日期**: 2025-11-01

**驗收標準**:
- ✅ `temp_line_id` 欄位從資料庫完全移除
- ✅ 所有 LINE 綁定邏輯使用 `line_user_id`
- ✅ API 回應不包含 `temp_line_id` 欄位
- ✅ 所有相關測試通過
- ✅ 文檔已更新 (3 個主要文檔)

**影響範圍**:
- Database: `users` 表約束修改
- ORM: `UserModel` 約束更新
- API: `patient.py` router 重構
- Docs: API、Database、Architecture 文檔更新

---

## 🔧 技術棧與工具

**資料庫**:
- PostgreSQL 15.14
- pgvector 0.5.0 (向量搜尋)
- Docker (respirally-postgres 容器)

**遷移工具**:
- Alembic 1.13+

**ORM**:
- SQLAlchemy 2.0+ (AsyncSession)

---

## 📝 後續建議

### 資料庫管理

1. **Schema 切換機制**:
   - 在應用程式中實作 schema 切換功能
   - 透過環境變數控制使用哪個 schema (development/production)

2. **Production Schema 資料填充**:
   - 當準備部署時，從 public schema 遷移生產資料到 production schema
   - 使用 `pg_dump` 和 `pg_restore` 進行資料遷移

3. **Development Schema AI 知識庫**:
   - 填充 `copd_knowledge_base` 表的 AI 訓練資料
   - 建立相關的查詢索引以提升效能

4. **資料備份策略**:
   - 建立定期備份機制
   - 特別是 production schema 的資料保護

### 技術債務

**TD-001**: Router 層違規重構 (Sprint 5)
- 狀態: ⏳ 待實作
- 優先級: P1
- 預估工時: 12h

**TD-003**: Domain Entity 完整實作 (Sprint 4-5)
- 狀態: ⏳ 待實作
- 優先級: P0
- 預估工時: 12h

---

## 📚 參考文件

**變更相關**:
- [Architecture Review Report](../.claude/context/docs/architecture_review_linus_20251101.md)
- [Database Schema Design v1.0](../database/schema_design_v1.0.md)
- [Database Status Report 2025-11-01](../database/database_status_2025_11_01.md)
- [API Design Specification](../06_api_design_specification.md)
- [Architecture and Design](../05_architecture_and_design.md)

**Migration 檔案**:
- `backend/alembic/versions/2025_11_01_0825-remove_temp_line_id_constraint.py`

**Git Commits**:
- `7359fbb` - fix(migration): update TD-002 migration dependencies
- `5514aa2` - docs(api): update PatientCreate schema for TD-002
- `20a3616` - docs(db): update users table constraints for TD-002
- `fd7a074` - docs(arch): add TD-002 fix to ADR and appendix
- `162c2fb` - docs(db): complete development and production schema setup

---

**文件作者**: Claude Code AI
**審核者**: Technical Lead
**最後更新**: 2025-11-01 11:53
