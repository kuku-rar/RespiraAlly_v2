# RespiraAlly API 設計規範

---

**文件版本:** `v1.0.0`
**最後更新:** `2025-10-16`
**主要作者:** `Claude Code AI`
**狀態:** `草稿 (Draft)`
**相關架構文件:** `[./architecture_and_design.md]`
**OpenAPI 定義文件:** `(待建立)`

---

## 1. 引言 (Introduction)

### 1.1 目的
為 `RespiraAlly V2.0` 的後端微服務提供統一、明確、易於遵循的 API 接口契約，確保前端、後端與跨服務間的高效協作。

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
    gender: Literal["male", "female", "other"]
    birth_date: date
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

### 7.3 `Patient360`
```python
class KPI(BaseModel):
    cat_score: Optional[int]
    mmrc_score: Optional[int]
    adherence_rate_7d: float
    risk_score: int

class TrendPoint(BaseModel):
    date: date
    value: float

class Patient360(Patient): # 繼承自基礎 Patient 模型
    kpis: KPI
    trends: Dict[str, List[TrendPoint]]
    event_timeline: List[Event]
```
