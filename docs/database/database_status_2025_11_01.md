# RespiraAlly 資料庫狀態報告

**資料庫**: respirally_db
**PostgreSQL 版本**: 15.14
**生成時間**: 2025-11-01
**最後更新**: 2025-11-01 11:47 (完成 development schema 外鍵添加)
**Docker 容器**: respirally-postgres (重啟驗證完成)  

---

## 📊 Schema 總覽

| Schema | 資料表數量 | 主鍵 | 外鍵 | 唯一約束 | 檢查約束 | 總約束數 |
|--------|-----------|------|------|---------|---------|---------|
| **public** | 6 | 6 | 5 | 4 | 12 | 27 |
| **development** | 7 | 7 | **5** ✅ | 4 | 12 | **28** |
| **production** | 6 | 6 | 5 | 4 | 12 | 27 |
| **test_data** | 6 | 6 | 5 | 4 | 9 | 24 |

---

## 📁 資料表分布

### Public Schema (主要應用程式 Schema)
- ✅ users
- ✅ patient_profiles
- ✅ therapist_profiles
- ✅ daily_logs
- ✅ event_logs
- ✅ survey_responses

### Development Schema
- ✅ users (空表)
- ✅ patient_profiles (空表)
- ✅ therapist_profiles (空表)
- ✅ daily_logs (空表)
- ✅ event_logs (空表)
- ✅ survey_responses (空表)
- ✅ copd_knowledge_base (空表)

### Production Schema
- ✅ users (空表)
- ✅ patient_profiles (空表)
- ✅ therapist_profiles (空表)
- ✅ daily_logs (空表)
- ✅ event_logs (空表)
- ✅ survey_responses (空表)

### Test Data Schema
- ✅ users
- ✅ patient_profiles
- ✅ therapist_profiles
- ✅ daily_logs
- ✅ event_logs
- ✅ survey_responses

---

## 🔗 外鍵約束狀態

### ✅ Public Schema (完整)
1. `daily_logs.patient_id` → `patient_profiles.user_id`
2. `patient_profiles.therapist_id` → `therapist_profiles.user_id`
3. `patient_profiles.user_id` → `users.user_id`
4. `survey_responses.patient_id` → `patient_profiles.user_id`
5. `therapist_profiles.user_id` → `users.user_id`

### ✅ Development Schema (完整)
**狀態**: 資料表結構已複製，外鍵約束已完整建立 (2025-11-01 11:47)

**外鍵約束**:
1. ✅ `daily_logs.patient_id` → `patient_profiles.user_id` (ON DELETE CASCADE)
2. ✅ `patient_profiles.therapist_id` → `therapist_profiles.user_id` (ON DELETE SET NULL)
3. ✅ `patient_profiles.user_id` → `users.user_id` (ON DELETE CASCADE)
4. ✅ `survey_responses.patient_id` → `patient_profiles.user_id` (ON DELETE CASCADE)
5. ✅ `therapist_profiles.user_id` → `users.user_id` (ON DELETE CASCADE)

### ✅ Production Schema (完整)
1. `daily_logs.patient_id` → `patient_profiles.user_id`
2. `patient_profiles.therapist_id` → `therapist_profiles.user_id`
3. `patient_profiles.user_id` → `users.user_id`
4. `survey_responses.patient_id` → `patient_profiles.user_id`
5. `therapist_profiles.user_id` → `users.user_id`

### ✅ Test Data Schema (完整)
與 public schema 相同的外鍵結構

---

## 📈 資料筆數統計

| Schema | users | patient_profiles | therapist_profiles | daily_logs | event_logs | survey_responses | 其他 |
|--------|-------|------------------|-------------------|------------|------------|-----------------|------|
| **public** | 1 | 0 | 0 | 0 | 0 | 0 | - |
| **development** | 0 | 0 | 0 | 0 | 0 | 0 | copd_kb: 0 |
| **production** | 0 | 0 | 0 | 0 | 0 | 0 | - |

---

## ✅ 關鍵發現

### 1. Development 和 Production Schema 結構完整 ✅
- **Development Schema**: 7 個表，28 個約束（包含 5 個外鍵）
- **Production Schema**: 6 個表，27 個約束（包含 5 個外鍵）
- **狀態**: 兩個 schema 的資料完整性保護機制已完整建立
- **更新**: 2025-11-01 11:47 完成 development schema 外鍵添加並驗證

### 2. Schema 用途與架構
- **public schema**: 主要應用程式 schema（Alembic migration 目標）
- **development schema**: 開發環境，包含額外的 `copd_knowledge_base` 表
- **production schema**: 生產環境，僅核心 6 表
- **test_data schema**: 測試資料 schema

### 3. 資料表分布說明
- **development schema**: 7 表（核心 6 表 + copd_knowledge_base）
- **其他 schema**: 6 表（僅核心應用程式表）
- **原因**: development schema 包含 AI 知識庫相關功能

---

## 🎯 已完成任務與後續建議

### ✅ 已完成 (2025-11-01)
1. ✅ 建立 production schema 並複製所有資料表結構（空表）
2. ✅ 為 production schema 添加完整的外鍵約束
3. ✅ 為 development schema 添加完整的外鍵約束
4. ✅ 驗證兩個 schema 的資料完整性保護機制
5. ✅ 重啟 PostgreSQL Docker 容器並驗證所有設定持久化

### 📋 後續建議
1. **Production Schema 資料填充**:
   - 當準備部署時，從 public schema 遷移生產資料到 production schema
   - 使用 `pg_dump` 和 `pg_restore` 進行資料遷移

2. **Development Schema AI 知識庫**:
   - 填充 `copd_knowledge_base` 表的 AI 訓練資料
   - 建立相關的查詢索引以提升效能

3. **Schema 切換機制**:
   - 在應用程式中實作 schema 切換功能
   - 透過環境變數控制使用哪個 schema (development/production)

4. **資料備份策略**:
   - 建立定期備份機制
   - 特別是 production schema 的資料保護

---

## 📝 技術細節

### TD-002 約束更新狀態
- ✅ `users_patient_line_check` 已從所有 schema 移除
- ✅ `users_login_method_check` 已在所有 schema 更新
- ✅ `users_therapist_email_check` 保持不變

### Alembic Migration 狀態
- Alembic 主要在 **public schema** 執行 migration
- development 和 production schema 是手動建立的副本

---

## 📜 更新記錄

### 2025-11-01 11:47 - Development Schema 外鍵完成
**執行動作**:
1. 為 development schema 添加 5 個外鍵約束
2. 驗證 development schema 結構完整性（28 個約束）
3. 重啟 PostgreSQL Docker 容器
4. 驗證重啟後所有 schema 設定持久化

**執行指令**:
```sql
-- 添加外鍵約束
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

**驗證結果**:
- ✅ Development schema: 7 表，5 外鍵，28 總約束
- ✅ Production schema: 6 表，5 外鍵，27 總約束
- ✅ 所有表為空（符合要求）
- ✅ Docker 容器重啟後設定持久化

**負責人**: Claude Code
**狀態**: 完成

