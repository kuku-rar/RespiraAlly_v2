# RespiraAlly V2.0 文件對齊報告

**報告日期**: 2025-10-18
**報告者**: Claude Code AI
**版本**: v1.0

---

## 執行摘要

本報告針對 RespiraAlly V2.0 專案的文件進行了全面對齊檢查,識別並修正了新生成文件(資料庫設計、API查詢範例、架構審視)與現有開發文件之間的資訊不一致問題。

**主要發現**:
- ✅ 識別出 **4 個主要資訊落差**
- ✅ 更新了 **4 份核心開發文件**
- ✅ 所有文件現已對齊至最新的資料庫設計

---

## 1. 新增資料庫功能總覽

### 1.1 病患基本資料擴展

**新增欄位** (patient_profiles 表):
- `hospital_medical_record_number` - 醫院病歷號
- `height_cm` - 身高 (cm)
- `weight_kg` - 體重 (kg)
- `smoking_status` - 吸菸狀態 (NEVER/FORMER/CURRENT)
- `smoking_years` - 吸菸年數

**相關資料庫物件**:
- ENUM 型別: `smoking_status_enum`
- 視圖: `patient_health_summary` (含 BMI 計算)
- 索引: `idx_patient_medical_record_number`, `idx_patient_smoking_status`
- 約束: 5 個 CHECK 約束保證數據完整性

### 1.2 KPI 快取層設計

**patient_kpi_cache 表擴展**:
- 新增 **11 個欄位**:
  - 基礎統計: `first_log_date`, `avg_water_intake_30d`, `avg_steps_7d/30d`
  - 最新問卷: `latest_cat_score`, `latest_cat_date`, `latest_mmrc_score/date`
  - 最新風險: `latest_risk_score`, `latest_risk_level`, `latest_risk_date`
  - 症狀統計: `symptom_occurrences_30d`

**新增資料視圖** (3 個):
1. `patient_kpi_windows` - 動態時間窗口 KPI (7/30/90天)
2. `patient_health_timeline` - 每日時間序列 (含移動平均)
3. `patient_survey_trends` - 問卷趨勢 (含分數變化)

**自動化機制**:
- **3 個觸發器**: 自動更新 KPI 快取
  - `trigger_update_kpi_on_daily_log_insert`
  - `trigger_update_kpi_on_survey_insert`
  - `trigger_update_kpi_on_risk_insert`
- **1 個存儲過程**: `refresh_patient_kpi_cache(patient_id)`

---

## 2. 文件對齊詳細報告

### 2.1 產品需求文件 (02_product_requirements_document.md)

**狀態**: ✅ 已更新

**變更內容**:

1. **新增使用者故事 US-103**:
   ```
   As a 新病患,
   I want to 在初次註冊時填寫基本健康資料（身高、體重、醫院病歷號、吸菸史）,
   so that 系統能計算 BMI 與風險評估。
   ```

   **允收標準**:
   - 支援輸入身高 (50-250 cm)、體重 (20-300 kg)
   - 醫院病歷號為選填
   - 吸菸史包含狀態與年數
   - 系統自動計算 BMI 並分級

2. **更新 US-202** (健康趨勢查看):
   - 新增: 支援顯示移動平均線平滑曲線

3. **新增 US-203** (核心健康 KPI 查看):
   ```
   As a 病患,
   I want to 查看我的核心健康 KPI（依從率、飲水量、運動量、問卷分數）,
   so that 快速了解整體健康狀況。
   ```

   **允收標準**:
   - KPI 資料從快取表讀取，查詢時間 < 50ms
   - 包含 7 日與 30 日依從率對比
   - 顯示最新 CAT/mMRC 問卷分數與日期
   - 顯示最新風險等級

4. **更新 US-205** (30日健康趨勢):
   - 新增: 支援顯示累積統計（總日誌數、總用藥次數）

---

### 2.2 架構與設計文件 (05_architecture_and_design.md)

**狀態**: ✅ 已更新

**變更內容**:

1. **新增 Section 5.3**: **KPI 快取層與資料視圖設計**

   **5.3.1 兩層式架構設計**:
   - 快取層 (Cache Layer): `patient_kpi_cache` 表
   - 視圖層 (View Layer): 4 個資料視圖
   - 包含完整的架構流程圖 (Mermaid)

   **5.3.2 patient_kpi_cache 表設計**:
   - 核心欄位說明
   - 更新機制 (觸發器 + 定期刷新)

   **5.3.3 資料視圖設計**:
   - 4 個視圖的用途與關鍵特性
   - 查詢性能目標

   **5.3.4 性能優化策略**:
   - 索引設計
   - 查詢性能目標
   - 降級策略

2. **更新 ER 圖** (Section 5.1):
   - 在 PATIENTS 實體中增加新欄位:
     - `hospital_medical_record_number`
     - `height_cm`, `weight_kg`
     - `smoking_status`, `smoking_years`

---

### 2.3 API 設計規範 (06_api_design_specification.md)

**狀態**: ✅ 已更新

**變更內容**:

1. **更新 PatientCreate Schema** (Section 7.1):
   ```python
   class PatientCreate(BaseModel):
       # ... 原有欄位 ...

       # 新增醫院整合資訊
       hospital_medical_record_number: Optional[str] = None

       # 新增體徵數據
       height_cm: Optional[conint(ge=50, le=250)] = None
       weight_kg: Optional[confloat(ge=20.0, le=300.0)] = None

       # 新增吸菸史
       smoking_status: Optional[Literal["NEVER", "FORMER", "CURRENT"]] = None
       smoking_years: Optional[conint(ge=0, le=100)] = None
   ```

2. **更新 Patient360 Schema** (Section 7.3):
   - 重新設計 `PatientKPI` 模型 (含所有新 KPI 欄位)
   - 新增 `TrendPoint` 模型 (含移動平均)
   - 新增 `SurveyTrend` 模型 (含分數變化)

3. **新增 API 端點** (Section 6.3):
   - `GET /patients/{patient_id}/kpis` - 查詢 KPI (< 50ms)
   - `GET /patients/{patient_id}/health-timeline` - 健康時間序列 (< 300ms)
   - `GET /patients/{patient_id}/survey-trends` - 問卷趨勢
   - `POST /patients/{patient_id}/kpis/refresh` - 手動刷新 KPI

---

### 2.4 模組規格與測試 (07_module_specification_and_tests.md)

**狀態**: ✅ 已更新

**變更內容**:

1. **更新風險引擎 `calculate_health_score` 函式**:

   **新增參數**:
   - `bmi: Optional[float]` - BMI 值
   - `smoking_years: Optional[int]` - 吸菸年數

   **更新核心公式**:
   ```
   S_base = 0.30×A₇ + 0.15×H₃₀ + 0.15×(100-N₃₀) + 0.15×(100-C) + 0.20×(100-R̂)

   調整項:
   - BMI 調整: -8 至 0 分
   - 吸菸年數調整: -10 至 0 分

   S_final = S_base + BMI_adjustment + Smoking_adjustment
   ```

2. **新增測試案例 TC-RiskEngine-006**:
   - 測試肥胖且長期吸菸者的風險計算

3. **新增模組**: **KPICalculationService**

   **規格 2**: `refresh_patient_kpi_cache`
   - 函式簽名
   - 契約式設計
   - 3 個測試案例 (單一刷新、批量刷新、錯誤處理)

   **規格 3**: `calculate_bmi`
   - BMI 計算與分級
   - 4 個測試案例 (正常、過輕、肥胖、邊界)

---

### 2.5 專案結構指南 (08_project_structure_guide.md)

**狀態**: ✅ 無需更新

**理由**:
- 此文件定義專案目錄結構與檔案組織
- 新增的資料庫變更不影響專案結構
- Modular Monolith 架構已涵蓋所有業務模組

---

## 3. 資訊對齊矩陣

| 新增功能 | DATABASE_SCHEMA_DESIGN | API_QUERY_EXAMPLES | 02_PRD | 05_ARCH | 06_API | 07_MODULE | 08_STRUCTURE |
|----------|------------------------|-------------------|--------|---------|--------|-----------|--------------|
| **病患健康資料欄位** | ✅ 完整定義 | ✅ 查詢範例 | ✅ US-103 | ✅ ER圖更新 | ✅ Schema更新 | ✅ 風險計算 | N/A |
| **patient_kpi_cache 擴展** | ✅ 完整定義 | ✅ 查詢範例 | ✅ US-203 | ✅ Section 5.3 | ✅ PatientKPI | ✅ KPI模組 | N/A |
| **patient_kpi_windows 視圖** | ✅ 完整定義 | ✅ 查詢範例 | ✅ US-203 | ✅ Section 5.3 | ✅ API端點 | ✅ 測試案例 | N/A |
| **patient_health_timeline 視圖** | ✅ 完整定義 | ✅ 查詢範例 | ✅ US-202/205 | ✅ Section 5.3 | ✅ API端點 | N/A | N/A |
| **patient_survey_trends 視圖** | ✅ 完整定義 | ✅ 查詢範例 | ✅ US-203 | ✅ Section 5.3 | ✅ API端點 | N/A | N/A |
| **patient_health_summary 視圖** | ✅ 完整定義 | ✅ 查詢範例 | ✅ US-103 | ✅ Section 5.3 | ✅ PatientCreate | ✅ BMI計算 | N/A |
| **觸發器 (3個)** | ✅ 完整定義 | N/A | N/A | ✅ Section 5.3 | N/A | ✅ 更新機制 | N/A |
| **存儲過程 refresh_patient_kpi_cache** | ✅ 完整定義 | N/A | N/A | ✅ Section 5.3 | ✅ API端點 | ✅ 規格+測試 | N/A |

**圖例**:
- ✅ 已包含或已更新
- N/A 不適用/無需包含

---

## 4. 重複資訊識別

### 4.1 DATABASE_SCHEMA_DESIGN.md vs ARCHITECTURE_REVIEW.md

**重複內容**:
- ARCHITECTURE_REVIEW.md 中的資料庫設計建議已整合至 DATABASE_SCHEMA_DESIGN.md
- ARCHITECTURE_REVIEW.md 中的索引設計建議已整合至 DATABASE_SCHEMA_DESIGN.md

**建議**: ✅ **保留 ARCHITECTURE_REVIEW.md**
- 理由: 此文件是架構審視報告,記錄了設計決策過程,具有歷史價值
- 性質: 一次性審視報告,非持續更新的設計文件

### 4.2 API_QUERY_EXAMPLES_FOR_FRONTEND.md vs 06_api_design_specification.md

**內容差異**:
- `API_QUERY_EXAMPLES`: 提供 **SQL 查詢範例** + **前端整合指南**
- `06_api_design_specification`: 定義 **RESTful API 契約** + **Pydantic Schema**

**建議**: ✅ **保留兩者,角色互補**
- `API_QUERY_EXAMPLES`: 供前端團隊參考 SQL 查詢邏輯
- `06_api_design_specification`: 供後端團隊實作 API 端點

### 4.3 DATABASE_SCHEMA_DESIGN.md vs 05_architecture_and_design.md

**內容差異**:
- `DATABASE_SCHEMA_DESIGN`: **詳細** 資料庫設計 (表結構、索引、觸發器、存儲過程)
- `05_architecture_and_design`: **概述** 資料架構 (ER 圖、數據流、KPI 快取層架構)

**建議**: ✅ **保留兩者,詳略互補**
- 05 文件: 整體架構視角,提供概覽
- DATABASE 文件: 實作層級,提供詳細 Schema

---

## 5. 建議的文件刪除/歸檔

**無需刪除文件**

所有文件都有其獨特價值:
- **DATABASE_SCHEMA_DESIGN.md**: 資料庫實作指南
- **API_QUERY_EXAMPLES_FOR_FRONTEND.md**: 前端查詢參考
- **ARCHITECTURE_REVIEW.md**: 架構審視歷史記錄
- **02_product_requirements_document.md**: 產品需求定義
- **05_architecture_and_design.md**: 整體架構設計
- **06_api_design_specification.md**: API 契約規範
- **07_module_specification_and_tests.md**: 模組規格與測試
- **08_project_structure_guide.md**: 專案結構指南

---

## 6. 對齊完成檢查清單

### 6.1 產品需求對齊
- [x] 病患基本健康資料需求已補充 (US-103)
- [x] KPI 視覺化需求已補充 (US-203)
- [x] 健康趨勢查看需求已更新 (US-202, US-205)

### 6.2 架構設計對齊
- [x] ER 圖已包含新欄位
- [x] KPI 快取層架構已說明
- [x] 資料視圖設計已說明
- [x] 性能目標已定義

### 6.3 API 設計對齊
- [x] PatientCreate Schema 已更新
- [x] Patient360 Schema 已重新設計
- [x] KPI 查詢端點已新增
- [x] 健康趨勢查詢端點已新增
- [x] 問卷趨勢查詢端點已新增

### 6.4 模組規格對齊
- [x] 風險計算公式已更新 (考慮 BMI、吸菸年數)
- [x] KPI 計算模組規格已新增
- [x] BMI 計算規格已新增
- [x] 相關測試案例已補充

### 6.5 資料庫實作對齊
- [x] 所有新增欄位已在 migration 腳本中定義
- [x] 所有視圖已在 migration 腳本中定義
- [x] 所有觸發器已在 migration 腳本中定義
- [x] 所有存儲過程已在 migration 腳本中定義

---

## 7. 後續行動建議

### 7.1 立即行動

1. **執行資料庫 Migration**:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **初始化 KPI 快取**:
   ```sql
   SELECT refresh_patient_kpi_cache();
   ```

3. **驗證視圖可用性**:
   ```sql
   SELECT * FROM patient_health_summary LIMIT 1;
   SELECT * FROM patient_kpi_windows LIMIT 1;
   SELECT * FROM patient_health_timeline LIMIT 1;
   SELECT * FROM patient_survey_trends LIMIT 1;
   ```

### 7.2 短期行動 (本週內)

1. **後端實作**:
   - 實作 `/patients/{id}/kpis` API 端點
   - 實作 `/patients/{id}/health-timeline` API 端點
   - 實作 `/patients/{id}/survey-trends` API 端點
   - 更新 `PatientCreate` 請求驗證邏輯

2. **前端整合**:
   - 根據 API_QUERY_EXAMPLES_FOR_FRONTEND.md 整合新端點
   - 實作 KPI Dashboard 組件
   - 實作健康趨勢折線圖組件
   - 實作問卷趨勢圖表組件

3. **測試**:
   - 執行模組規格中定義的所有測試案例
   - 驗證 API 性能目標 (KPI < 50ms, Timeline < 300ms)

### 7.3 中期行動 (本月內)

1. **效能監控**:
   - 建立 KPI 快取命中率監控
   - 建立視圖查詢性能監控
   - 設定性能告警 (超過目標值時通知)

2. **自動化任務**:
   - 設定 pg_cron 定期執行 `refresh_patient_kpi_cache()`
   - 建議頻率: 每小時執行一次

3. **文件維護**:
   - 將所有 ADR (架構決策記錄) 補充完整
   - 建立 API 文檔 (Swagger/OpenAPI)
   - 更新部署文檔包含新的資料庫 migration 步驟

---

## 8. 文件版本控制建議

**建議文件版本更新**:

| 文件名稱 | 當前版本 | 建議版本 | 理由 |
|----------|----------|----------|------|
| 02_product_requirements_document.md | v2.0 | v2.1 | 新增 3 個使用者故事 |
| 05_architecture_and_design.md | v2.0 | v2.1 | 新增 KPI 快取層設計 |
| 06_api_design_specification.md | v1.0.0 | v1.1.0 | 新增 4 個 API 端點 + 更新 Schema |
| 07_module_specification_and_tests.md | v1.0 | v1.1 | 新增 KPI 模組規格 + 更新風險計算 |
| DATABASE_SCHEMA_DESIGN.md | v1.0 | v1.1 | 新增 KPI 快取表、視圖、觸發器 |

---

## 9. 總結

✅ **對齊完成度**: 100%

**已完成**:
- 識別並修正所有資訊不一致
- 更新 4 份核心開發文件
- 建立完整的資訊對齊矩陣
- 提供後續行動建議

**文件狀態**:
- 所有文件已對齊至最新資料庫設計
- 無需刪除任何文件 (角色互補)
- 建議更新文件版本號以反映變更

**下一步**:
- 等待用戶確認對齊報告
- 執行資料庫 Migration
- 開始後端 API 實作
- 開始前端整合工作

---

**報告結束**

**簽署**: Claude Code AI
**日期**: 2025-10-18
