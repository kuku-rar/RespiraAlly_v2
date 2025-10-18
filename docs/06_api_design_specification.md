# RespiraAlly API 設計規範

---

**文件版本:** `v1.0.0`
**最後更新:** `2025-10-18`
**主要作者:** `Claude Code AI`
**狀態:** `草稿 (Draft)`

**相關文檔:**
- **系統架構:** [./05_architecture_and_design.md](./05_architecture_and_design.md) - 整體架構設計
- **資料庫設計:** [./DATABASE_SCHEMA_DESIGN.md](./DATABASE_SCHEMA_DESIGN.md) - 資料庫結構與設計
- **前端架構:** [./12_frontend_architecture_specification.md](./12_frontend_architecture_specification.md) - 前端技術棧與規範
- **前端信息架構:** [./17_frontend_information_architecture_template.md](./17_frontend_information_architecture_template.md) - 前端頁面結構與路由
- **OpenAPI 定義文件:** `(待建立)`

---

## 1. 引言 (Introduction)

### 1.1 目的
為 `RespiraAlly V2.0` 的**後端服務**提供統一、明確、易於遵循的 **API 接口契約**，定義後端 FastAPI 應用的所有 HTTP/WebSocket 端點、請求/回應格式、認證授權機制、錯誤處理策略,確保前端與後端間的高效協作。

**本文檔專注於後端服務責任:**
- ✅ 後端 API 端點設計 (RESTful API、WebSocket)
- ✅ 請求/回應數據模型 (Pydantic Schemas)
- ✅ 認證授權機制 (JWT、RBAC)
- ✅ 錯誤處理與狀態碼
- ✅ 後端性能要求 (P95 < 500ms)

**本文檔不包含:**
- ❌ 前端 UI/UX 設計 (參考前端架構文件)
- ❌ 前端頁面路由 (參考 17_frontend_information_architecture_template.md)
- ❌ 前端狀態管理 (參考 12_frontend_architecture_specification.md)

**架構說明**: 基於 [ARCHITECTURE_REVIEW.md](./ARCHITECTURE_REVIEW.md) 的建議，**MVP 階段 (Phase 0-2) 採用 Modular Monolith 架構**，所有業務模組（auth, patients, daily_logs, voice 等）運行在同一個 FastAPI 應用實例中。Phase 3 後可根據實際需求拆分為微服務。

### 1.2 快速入門
*   **第 1 步: 獲取 Access Token**
    *   治療師通過 `POST /auth/token` 端點使用 Email 和密碼登入獲取。
    *   病患通過 LINE LIFF 登入流程自動獲取。
*   **第 2 步: 發送您的第一個請求**
    ```bash
    curl -X GET 'https://api.respira.ally/v1/health' \
    -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
    ```
*   **預期回應:**
    ```json
    { "status": "ok" }
    ```

---

## 2. 設計原則與約定

### 2.1 API 風格
*   **風格:** RESTful API。
*   **核心原則:** 資源導向、無狀態、標準 HTTP 方法。

### 2.2 基本 URL
*   **生產環境:** `https://api.respira.ally/v1`
*   **預備環境:** `https://staging-api.respira.ally/v1`

### 2.3 請求與回應格式
*   **格式:** `application/json` (UTF-8 編碼)。

### 2.4 標準 HTTP Headers
*   **所有請求:**
    *   `Authorization: Bearer <access_token>`: 包含認證用的 JWT。
    *   `X-Request-ID`: 用於追蹤請求的唯一 ID (UUID)。
*   **所有回應:**
    *   `X-Request-ID`: 從請求傳入或由伺服器生成的唯一 ID。
*   **冪等性請求 (POST):**
    *   `Idempotency-Key`: 用於保證 POST 請求的冪等性。

### 2.5 命名約定
*   **資源路徑:** 小寫，多個單詞用連字符 `-` 連接，名詞複數形式 (e.g., `/daily-logs`)。
*   **JSON 欄位 & 查詢參數:** `snake_case` (e.g., `patient_id`, `page_size`)。

### 2.6 日期與時間格式
*   所有日期時間字段均使用 **ISO 8601** 格式，並包含 UTC 時區標識 (e.g., `2025-10-16T12:00:00Z`)。

---

## 3. 認證與授權

*   **認證機制:** JWT (JSON Web Tokens)。Access Token 有效期 8 小時，Refresh Token 有效期 30 天。
*   **授權模型:** 基於角色的訪問控制 (RBAC)。定義的角色至少包括 `patient`, `therapist`, `admin`。部分端點會檢查資源所有權（例如，病患只能存取自己的日誌）。

---

## 4. 通用 API 行為

### 4.1 分頁
*   **策略:** 基於偏移量 (Offset-based) 的分頁。
*   **查詢參數:** `skip` (預設 0), `limit` (預設 20，最大 100)。
*   **回應結構:**
    ```json
    {
      "total": 120,
      "items": [ ... ],
      "skip": 0,
      "limit": 20
    }
    ```

### 4.2 排序
*   **查詢參數:** `sort_by` (e.g., `sort_by=-risk_score` 表示按風險分數降序)。

### 4.3 過濾
*   直接使用欄位名作為查詢參數 (e.g., `/patients?risk_bucket=high`)。

---

## 5. 錯誤處理

### 5.1 標準錯誤回應格式
```json
{
  "detail": {
    "type": "validation_error",
    "code": "parameter_missing",
    "message": "Field required",
    "loc": ["body", "name"]
  }
}
```
*註: 此結構遵循 FastAPI 的預設錯誤格式。*

### 5.2 通用 HTTP 狀態碼
*   `200 OK`, `201 Created`, `204 No Content`
*   `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`
*   `500 Internal Server Error`

---

## 6. API 端點詳述

### 6.1 資源：認證 (Auth)

#### `POST /auth/register` (病患註冊)
*   **描述:** 透過 LINE LIFF 註冊新病患。
*   **請求體:** `PatientCreate`
*   **成功回應 (201 Created):** `TokenResponse`

#### `POST /auth/token` (治療師登入)
*   **描述:** 治療師使用 Email/密碼登入獲取 Token。
*   **請求體:** `OAuth2PasswordRequestForm`
*   **成功回應 (200 OK):** `TokenResponse`

### 6.2 資源：日誌 (Daily Logs)

*   **資源路徑:** `/daily-logs`

#### `POST /daily-logs` (提交日誌)
*   **描述:** 病患提交當日的健康日誌。若當日已存在記錄，則更新。
*   **授權:** `patient` 角色，且為資源所有者。
*   **請求體:** `DailyLogCreate`
*   **成功回應 (201 Created 或 200 OK):** `DailyLog`
*   **冪等性:** 支持。

### 6.3 資源：病患 (Patients)

*   **資源路徑:** `/patients`

#### `GET /patients` (查詢病患列表)
*   **描述:** 治療師查詢其負責的病患列表，支援篩選、排序、分頁。
*   **授權:** `therapist` 角色。
*   **查詢參數:** `risk_bucket`, `adherence_rate_lte`, `last_active_gte`, `sort_by`, `skip`, `limit`
*   **成功回應 (200 OK):** `PatientListResponse`

#### `GET /patients/{patient_id}` (查詢病患 360° 檔案)
*   **描述:** 治療師查詢單一病患的完整檔案。
*   **授權:** `therapist` 角色，且為該病患的負責人。
*   **成功回應 (200 OK):** `Patient360`

#### `GET /patients/{patient_id}/kpis` (查詢病患 KPI)
*   **描述:** 查詢病患的 KPI 快取資料 (依從率、健康指標、最新問卷等)。
*   **授權:** `patient` (自己) 或 `therapist` (負責該病患)。
*   **查詢參數:**
    *   `refresh` (可選): 若為 `true`,先刷新 KPI 快取再返回
*   **成功回應 (200 OK):** `PatientKPI`
*   **性能要求:** < 50ms (直接查詢 patient_kpi_cache 表)

#### `GET /patients/{patient_id}/health-timeline` (查詢健康時間序列)
*   **描述:** 查詢病患的每日健康數據時間序列 (用於前端折線圖)。
*   **授權:** `patient` (自己) 或 `therapist` (負責該病患)。
*   **查詢參數:**
    *   `days` (可選): 返回近 N 天數據,預設 30,最大 90
    *   `include_ma` (可選): 是否包含移動平均線,預設 true
*   **成功回應 (200 OK):** `List[TrendPoint]`
*   **性能要求:** < 300ms (查詢 patient_health_timeline 視圖)

#### `GET /patients/{patient_id}/survey-trends` (查詢問卷趨勢)
*   **描述:** 查詢病患的 CAT/mMRC 問卷歷史趨勢。
*   **授權:** `patient` (自己) 或 `therapist` (負責該病患)。
*   **查詢參數:**
    *   `survey_type` (可選): 篩選問卷類型 ("CAT" 或 "mMRC"),不提供則返回所有
    *   `limit` (可選): 最多返回 N 筆,預設 10
*   **成功回應 (200 OK):** `List[SurveyTrend]`

#### `POST /patients/{patient_id}/kpis/refresh` (刷新病患 KPI 快取)
*   **描述:** 手動觸發 KPI 快取刷新 (調用 `refresh_patient_kpi_cache` 存儲過程)。
*   **授權:** `therapist` 角色。
*   **成功回應 (200 OK):**
    ```json
    {
      "message": "KPI cache refreshed successfully",
      "patient_id": "patient-uuid",
      "refreshed_at": "2025-10-18T10:30:00Z"
    }
    ```

### 6.4 資源：語音 (Voice)

*   **資源路徑:** `/voice`

#### `POST /voice/upload` (上傳語音)
*   **描述:** 病患上傳語音檔案以進行 AI 提問。此為異步處理。
*   **授權:** `patient` 角色。
*   **請求:** `multipart/form-data`，包含音訊檔案。
*   **成功回應 (202 Accepted):**
    ```json
    {
      "task_id": "some-unique-task-id",
      "status": "processing",
      "websocket_url": "wss://api.respira.ally/v1/ws/voice/some-unique-task-id"
    }
    ```

#### `WS /ws/voice/{task_id}` (接收語音處理結果)
*   **描述:** 用於接收語音任務處理結果的 WebSocket 端點。

---

## 7. 資料模型 (Pydantic Schemas)

### 7.1 `PatientCreate`
```python
class PatientCreate(BaseModel):
    line_user_id: str
    name: str
    gender: Literal["MALE", "FEMALE", "OTHER"]
    birth_date: date

    # 醫院整合資訊
    hospital_medical_record_number: Optional[str] = None

    # 體徵數據
    height_cm: Optional[conint(ge=50, le=250)] = None
    weight_kg: Optional[confloat(ge=20.0, le=300.0)] = None

    # 吸菸史
    smoking_status: Optional[Literal["NEVER", "FORMER", "CURRENT"]] = None
    smoking_years: Optional[conint(ge=0, le=100)] = None

    # 聯絡資訊
    phone: Optional[str] = None
```

### 7.2 `DailyLogCreate`
```python
class DailyLogCreate(BaseModel):
    med_taken: bool
    water_ml: conint(ge=0)
    exercise_min: conint(ge=0)
    cigarette_count: conint(ge=0)
```

### 7.3 `PatientKPI`
```python
class PatientKPI(BaseModel):
    """病患 KPI 快取資料 - 從 patient_kpi_cache 表查詢"""
    total_logs_count: int
    first_log_date: Optional[date]
    last_log_date: Optional[date]

    # 依從率
    adherence_rate_7d: Optional[int]  # 百分比 0-100
    adherence_rate_30d: Optional[int]

    # 健康指標
    avg_water_intake_7d: Optional[int]
    avg_water_intake_30d: Optional[int]
    avg_steps_7d: Optional[int]
    avg_steps_30d: Optional[int]

    # 最新問卷
    latest_cat_score: Optional[int]
    latest_cat_date: Optional[date]
    latest_mmrc_score: Optional[int]
    latest_mmrc_date: Optional[date]

    # 最新風險
    latest_risk_score: Optional[int]
    latest_risk_level: Optional[Literal["LOW", "MEDIUM", "HIGH"]]
    latest_risk_date: Optional[date]

    # 症狀統計
    symptom_occurrences_30d: int

    last_calculated_at: datetime

class TrendPoint(BaseModel):
    log_date: date
    medication_taken: Optional[bool]
    water_intake_ml: Optional[int]
    steps_count: Optional[int]
    water_intake_7d_ma: Optional[float]  # 移動平均
    steps_7d_ma: Optional[float]

class SurveyTrend(BaseModel):
    survey_type: str
    submitted_at: datetime
    total_score: int
    severity_level: str
    score_change: Optional[int]  # 與上次的差異
    score_change_from_baseline: Optional[int]  # 與首次的差異

class Patient360(Patient): # 繼承自基礎 Patient 模型
    kpis: PatientKPI
    health_timeline: List[TrendPoint]  # 近 30 日每日數據
    survey_trends: List[SurveyTrend]   # 問卷歷史
    event_timeline: List[Event]
```
