# API 開發檢查清單 - 病患註冊 API

> **API 端點**: POST /api/v1/auth/patient/register
> **負責人**: Claude Code AI
> **Sprint**: Sprint 4
> **開始日期**: 2025-10-25
> **目標完成日期**: 2025-10-25

---

## 📋 使用說明

1. 複製此模板到新的檔案
2. 填寫功能名稱和基本資訊
3. 按順序完成每個檢查項目
4. 所有項目完成後才能標記為「已完成」
5. 發現問題立即記錄到「問題追蹤」區塊

---

## 1. 需求分析 (Requirements Analysis)

### 1.1 功能描述
```
實作病患初次註冊 API，接收來自 LIFF 前端的完整病患資料（包含 LINE 認證資料、基本資料、
醫院病歷號、身體健康數據、急救聯絡人等），並儲存至資料庫。此 API 解決目前前端調用
/auth/patient/register 時收到 404 的問題，並支援醫院病歷號（hospital_patient_id）欄位。
```

### 1.2 使用者故事
```
作為 COPD 病患
我想要在初次使用 LINE LIFF 應用時完成詳細的註冊資訊填寫
以便醫療團隊能夠掌握我的完整健康狀況並提供個人化的照護
```

### 1.3 驗收標準
- [ ] 標準1: 前端成功提交包含所有欄位（包括 hospital_patient_id）的註冊請求
- [ ] 標準2: 後端成功驗證所有必填欄位並接收請求
- [ ] 標準3: 資料成功儲存至 users 和 patient_profiles 兩張表
- [ ] 標準4: hospital_patient_id 正確對應到資料庫的 hospital_medical_record_number 欄位
- [ ] 標準5: 回傳包含 JWT token 的登入回應，讓使用者可直接登入
- [ ] 標準6: 前端收到成功回應並導航至主頁
- [ ] 標準7: 所有欄位的資料流驗證（Form → API → DB → Display）100% 一致

### 1.4 資料欄位定義

| 欄位名稱 | 資料型別 | 必填/選填 | 驗證規則 | 說明 |
|---------|---------|---------|---------|------|
| line_user_id | string | 必填 | min:1, max:100 | LINE 使用者 ID |
| line_display_name | string | 選填 | max:100 | LINE 顯示名稱 |
| line_picture_url | string | 選填 | URL format | LINE 頭像 URL |
| full_name | string | 必填 | min:2, max:100 | 病患姓名 |
| date_of_birth | date | 必填 | ISO 8601 (YYYY-MM-DD) | 出生日期 |
| gender | enum | 必填 | MALE/FEMALE/OTHER | 性別 |
| phone_number | string | 選填 | max:20 | 聯絡電話 |
| hospital_patient_id | string | 選填 | max:50 | 醫院病歷號（對應 DB 的 hospital_medical_record_number） |
| height_cm | integer | 選填 | ge:100, le:250 | 身高（公分） |
| weight_kg | decimal | 選填 | ge:30, le:200 | 體重（公斤） |
| smoking_years | integer | 選填 | ge:0, le:80 | 吸菸年數 |
| emergency_contact_name | string | 選填 | max:100 | 緊急聯絡人姓名 |
| emergency_contact_phone | string | 選填 | max:20 | 緊急聯絡人電話 |

---

## 2. 後端實作 (Backend Implementation)

### 2.1 資料庫 Model (SQLAlchemy)

**檔案路徑**: `backend/src/respira_ally/infrastructure/database/models/[model_name].py`

- [ ] Model 類別定義
  ```python
  class [ModelName]Model(Base):
      __tablename__ = "[table_name]"

      # 欄位定義
      field1: Mapped[str] = mapped_column(String(100), nullable=False)
      field2: Mapped[int | None] = mapped_column(Integer, nullable=True)
  ```
- [ ] 主鍵 (Primary Key) 定義
- [ ] 外鍵 (Foreign Key) 定義
- [ ] 關聯關係 (Relationships) 定義
- [ ] 索引 (Indexes) 定義
- [ ] 約束條件 (Constraints) 定義
- [ ] `__repr__` 方法實作

**檢查點**:
- [ ] 欄位型別與需求一致
- [ ] 欄位 nullable 設定正確
- [ ] 關聯關係雙向設定
- [ ] 索引設定合理

### 2.2 Pydantic Schemas

**檔案路徑**: `backend/src/respira_ally/core/schemas/[schema_name].py`

#### 2.2.1 Request Schema
- [ ] Base Schema 定義
  ```python
  class [Feature]Base(BaseModel):
      field1: str = Field(..., min_length=2, max_length=100)
      field2: int | None = Field(None, ge=0, le=100)
  ```
- [ ] Create Schema 定義
  ```python
  class [Feature]Create([Feature]Base):
      # 額外的 create 欄位
      pass
  ```
- [ ] Update Schema 定義
  ```python
  class [Feature]Update(BaseModel):
      # 所有欄位都是 optional
      field1: str | None = Field(None, min_length=2, max_length=100)
  ```

**檢查點**:
- [ ] 所有必填欄位有 `...` 標記
- [ ] 驗證規則與需求一致 (min/max, ge/le, regex)
- [ ] Field 有適當的 description
- [ ] Enum 使用正確

#### 2.2.2 Response Schema
- [ ] Response Schema 定義
  ```python
  class [Feature]Response([Feature]Base):
      id: UUID
      created_at: datetime
      updated_at: datetime

      model_config = ConfigDict(from_attributes=True)
  ```
- [ ] List Response Schema
  ```python
  class [Feature]ListResponse(BaseModel):
      items: list[[Feature]Response]
      total: int
      page: int
      page_size: int
  ```

**檢查點**:
- [ ] Response 欄位與 Model 對應
- [ ] 敏感資料已過濾 (password, token)
- [ ] `model_config = ConfigDict(from_attributes=True)` 已設定
- [ ] 計算欄位邏輯正確

### 2.3 Repository Layer

**檔案路徑**: `backend/src/respira_ally/infrastructure/repository_impls/[feature]_repository_impl.py`

- [ ] Repository Interface 定義 (domain/repositories/)
  ```python
  class [Feature]Repository(ABC):
      @abstractmethod
      async def create([Feature]CreateData) -> [Feature]Model: ...

      @abstractmethod
      async def find_by_id(id: UUID) -> [Feature]Model | None: ...
  ```
- [ ] Repository Implementation
  ```python
  class [Feature]RepositoryImpl([Feature]Repository):
      def __init__(self, db: AsyncSession): ...

      async def create(...): ...
      async def find_by_id(...): ...
      async def find_all(...): ...
      async def update(...): ...
      async def delete(...): ...
  ```

**必要方法**:
- [ ] `create()` - 建立記錄
- [ ] `find_by_id()` - 根據 ID 查詢
- [ ] `find_all()` - 列表查詢（含分頁）
- [ ] `update()` - 更新記錄
- [ ] `delete()` - 刪除記錄（軟刪除/硬刪除）

**額外方法** (根據需求):
- [ ] `find_by_[field]()` - 根據特定欄位查詢
- [ ] `count()` - 計數
- [ ] `exists()` - 存在性檢查

**檢查點**:
- [ ] 所有方法有型別提示
- [ ] 所有方法有 docstring
- [ ] 異常處理完善
- [ ] 事務處理正確 (commit/rollback)

### 2.4 Use Case / Service Layer

**檔案路徑**: `backend/src/respira_ally/application/[feature]/use_cases/[action]_use_case.py`

- [ ] Use Case 類別定義
  ```python
  class [Action][Feature]UseCase:
      def __init__(self, repository: [Feature]Repository): ...

      async def execute(...) -> ...: ...
  ```
- [ ] 業務邏輯實作
  - [ ] 資料驗證
  - [ ] 業務規則檢查
  - [ ] 資料轉換
  - [ ] 異常處理
- [ ] Domain Events 發布 (如需要)
  ```python
  await event_bus.publish([Feature]CreatedEvent(...))
  ```

**檢查點**:
- [ ] 業務邏輯與資料存取分離
- [ ] 錯誤訊息清晰具體
- [ ] 所有異常情境都有處理
- [ ] 權限檢查完整

### 2.5 API Router

**檔案路徑**: `backend/src/respira_ally/api/v1/routers/[feature].py`

- [ ] Router 定義
  ```python
  router = APIRouter(prefix="/[feature]s", tags=["[Feature] Management"])
  ```
- [ ] Dependency Injection 函式
  ```python
  def get_[feature]_repository(db: AsyncSession = Depends(get_db)): ...
  def get_[action]_use_case(repo = Depends(get_[feature]_repository)): ...
  ```
- [ ] API 端點實作
  - [ ] POST `/[feature]s` - Create
  - [ ] GET `/[feature]s/{id}` - Read
  - [ ] GET `/[feature]s` - List
  - [ ] PATCH `/[feature]s/{id}` - Update
  - [ ] DELETE `/[feature]s/{id}` - Delete

**端點檢查項目** (每個端點):
- [ ] HTTP 方法正確
- [ ] 路徑參數正確
- [ ] Query 參數正確
- [ ] Request Body 型別正確
- [ ] Response Model 正確
- [ ] Status Code 正確
- [ ] 權限控制 (Depends)
- [ ] OpenAPI 文檔
  - [ ] summary
  - [ ] description
  - [ ] tags
  - [ ] response_model

**範例端點實作**:
```python
@router.post(
    "/",
    response_model=[Feature]Response,
    status_code=status.HTTP_201_CREATED,
    summary="Create [Feature]",
    description="詳細說明...",
    tags=["[Feature] Management"],
)
async def create_[feature](
    request: [Feature]CreateRequest,
    current_user: TokenData = Depends(get_current_user),
    use_case: [Action]UseCase = Depends(get_[action]_use_case),
) -> [Feature]Response:
    """端點文檔字串"""
    return await use_case.execute(...)
```

### 2.6 單元測試

**檔案路徑**: `backend/tests/unit/[feature]/test_[module].py`

#### Repository Tests
- [ ] `test_create_[feature]_success()`
- [ ] `test_find_by_id_success()`
- [ ] `test_find_by_id_not_found()`
- [ ] `test_find_all_with_pagination()`
- [ ] `test_update_[feature]_success()`
- [ ] `test_delete_[feature]_success()`

#### Use Case Tests
- [ ] `test_[action]_success()`
- [ ] `test_[action]_validation_error()`
- [ ] `test_[action]_business_rule_violation()`
- [ ] `test_[action]_permission_denied()`
- [ ] `test_[action]_not_found()`

**測試覆蓋率目標**: > 80%

**檢查點**:
- [ ] 所有 Repository 方法都有測試
- [ ] 所有 Use Case 都有測試
- [ ] 正常情境測試
- [ ] 異常情境測試
- [ ] 邊界值測試
- [ ] Mock 使用正確

### 2.7 API 整合測試

**檔案路徑**: `backend/tests/integration/api/test_[feature]_api.py`

#### HTTP Status Code Tests
- [ ] `test_create_[feature]_201_created()`
- [ ] `test_get_[feature]_200_ok()`
- [ ] `test_get_[feature]_404_not_found()`
- [ ] `test_list_[feature]s_200_ok()`
- [ ] `test_update_[feature]_200_ok()`
- [ ] `test_update_[feature]_404_not_found()`
- [ ] `test_delete_[feature]_204_no_content()`
- [ ] `test_create_[feature]_400_validation_error()`
- [ ] `test_create_[feature]_401_unauthorized()`
- [ ] `test_update_[feature]_403_forbidden()`

#### Business Logic Tests
- [ ] `test_create_duplicate_returns_error()`
- [ ] `test_update_with_invalid_data()`
- [ ] `test_delete_cascades_correctly()`
- [ ] `test_pagination_works_correctly()`
- [ ] `test_filtering_works_correctly()`

**檢查點**:
- [ ] 所有端點都有測試
- [ ] 測試使用實際資料庫 (TestClient + 測試資料庫)
- [ ] 測試資料使用 Faker 或 Factory
- [ ] 測試資料清理 (teardown)

---

## 3. 前端實作 (Frontend Implementation)

### 3.1 TypeScript Types 定義

**檔案路徑**: `frontend/[app]/src/types/[feature].ts`

- [ ] Request Type 定義
  ```typescript
  export interface [Feature]CreateRequest {
    field1: string
    field2?: number
  }

  export interface [Feature]UpdateRequest {
    field1?: string
    field2?: number
  }
  ```
- [ ] Response Type 定義
  ```typescript
  export interface [Feature]Response {
    id: string
    field1: string
    field2: number | null
    createdAt: string
    updatedAt: string
  }

  export interface [Feature]ListResponse {
    items: [Feature]Response[]
    total: number
    page: number
    pageSize: number
  }
  ```
- [ ] Enum 定義
  ```typescript
  export enum [Feature]Status {
    ACTIVE = 'ACTIVE',
    INACTIVE = 'INACTIVE',
  }
  ```

**檢查點**:
- [ ] 型別名稱與後端一致
- [ ] 欄位名稱與後端一致 (camelCase)
- [ ] 欄位型別與後端對應
- [ ] Optional 欄位標記正確 (`?`)
- [ ] Enum 值與後端一致

### 3.2 API Client 函式

**檔案路徑**: `frontend/[app]/src/api/[feature].ts`

- [ ] API Client 實作
  ```typescript
  export const [feature]Api = {
    // Create
    async create(data: [Feature]CreateRequest): Promise<[Feature]Response> {
      return apiClient.post<[Feature]Response>('/[feature]s', data)
    },

    // Read
    async getById(id: string): Promise<[Feature]Response> {
      return apiClient.get<[Feature]Response>(`/[feature]s/${id}`)
    },

    // List
    async list(params: ListParams): Promise<[Feature]ListResponse> {
      return apiClient.get<[Feature]ListResponse>('/[feature]s', { params })
    },

    // Update
    async update(id: string, data: [Feature]UpdateRequest): Promise<[Feature]Response> {
      return apiClient.patch<[Feature]Response>(`/[feature]s/${id}`, data)
    },

    // Delete
    async delete(id: string): Promise<void> {
      return apiClient.delete(`/[feature]s/${id}`)
    },
  }
  ```

**檢查點**:
- [ ] API 端點路徑與後端一致
- [ ] HTTP 方法正確
- [ ] Request 型別正確
- [ ] Response 型別正確
- [ ] 錯誤處理完整
- [ ] Mock 模式支援 (如需要)

### 3.3 React Hook (如使用 React Query)

**檔案路徑**: `frontend/[app]/src/hooks/use[Feature].ts`

- [ ] Query Hook
  ```typescript
  export function use[Feature](id: string) {
    return useQuery({
      queryKey: ['[feature]', id],
      queryFn: () => [feature]Api.getById(id),
    })
  }

  export function use[Feature]List(params: ListParams) {
    return useQuery({
      queryKey: ['[feature]s', params],
      queryFn: () => [feature]Api.list(params),
    })
  }
  ```
- [ ] Mutation Hook
  ```typescript
  export function useCreate[Feature]() {
    const queryClient = useQueryClient()

    return useMutation({
      mutationFn: [feature]Api.create,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['[feature]s'] })
      },
    })
  }
  ```

**檢查點**:
- [ ] Query Key 命名一致
- [ ] 快取策略合理
- [ ] Invalidation 邏輯正確
- [ ] Loading 狀態處理
- [ ] Error 狀態處理

### 3.4 UI Components

**檔案路徑**: `frontend/[app]/src/components/[Feature]/[ComponentName].tsx`

#### 3.4.1 表單 Component
- [ ] 表單欄位實作
  - [ ] 欄位1: [field1]
  - [ ] 欄位2: [field2]
  - [ ] 欄位3: [field3]
- [ ] 表單驗證
  - [ ] 必填欄位驗證
  - [ ] 格式驗證 (email, phone, etc.)
  - [ ] 範圍驗證 (min/max)
  - [ ] 自訂驗證邏輯
- [ ] 錯誤訊息顯示
  - [ ] 欄位級錯誤
  - [ ] 表單級錯誤
  - [ ] API 錯誤

**檢查點**:
- [ ] 表單欄位與 Schema 對應
- [ ] 驗證規則與後端一致
- [ ] 錯誤訊息使用者友善
- [ ] Loading 狀態處理
- [ ] 成功狀態處理

#### 3.4.2 列表 Component
- [ ] 資料顯示
- [ ] 分頁功能
- [ ] 篩選功能
- [ ] 排序功能
- [ ] 操作按鈕 (編輯/刪除)

#### 3.4.3 詳情 Component
- [ ] 資料顯示
- [ ] 編輯功能
- [ ] 刪除確認

### 3.5 Mock 資料 (開發用)

**檔案路徑**: `frontend/[app]/src/mocks/[feature].ts`

- [ ] Mock 資料定義
  ```typescript
  export const MOCK_[FEATURE]: [Feature]Response = {
    id: '00000000-0000-0000-0000-000000000001',
    field1: 'Mock Value',
    field2: 100,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
  ```
- [ ] Mock API 回應
  ```typescript
  if (isMockMode) {
    await new Promise(resolve => setTimeout(resolve, 1000))
    return MOCK_[FEATURE]
  }
  ```

**檢查點**:
- [ ] Mock 資料格式與 Schema 一致
- [ ] 包含成功情境
- [ ] 包含失敗情境 (如需要)

---

## 4. 整合驗證 (Integration Verification)

### 4.1 資料流驗證

- [ ] **前端 → 後端**
  - [ ] 前端表單送出資料格式正確
  - [ ] 後端成功接收資料
  - [ ] 資料驗證通過
- [ ] **後端 → 資料庫**
  - [ ] 資料正確寫入資料庫
  - [ ] 欄位型別正確
  - [ ] 關聯關係正確
  - [ ] 約束條件生效
- [ ] **資料庫 → 後端 → 前端**
  - [ ] 資料正確讀取
  - [ ] 資料轉換正確
  - [ ] 前端正確顯示

### 4.2 欄位對齊檢查

| 前端欄位 (camelCase) | API Request (camelCase) | 資料庫欄位 (snake_case) | 型別一致 | ✓/✗ |
|---------------------|------------------------|------------------------|---------|-----|
| field1 | field1 | field1 | string → String(100) | ✓ |
| field2 | field2 | field2 | number → Integer | ✓ |
| field3 | field3 | field3 | string → Date | ✓ |

### 4.3 E2E 測試

**檔案路徑**: `frontend/[app]/e2e/[feature].spec.ts`

- [ ] 建立流程測試
  ```typescript
  test('should create [feature] successfully', async ({ page }) => {
    // 1. 導航到建立頁面
    // 2. 填寫表單
    // 3. 送出表單
    // 4. 驗證成功訊息
    // 5. 驗證資料顯示
  })
  ```
- [ ] 列表流程測試
- [ ] 更新流程測試
- [ ] 刪除流程測試
- [ ] 錯誤情境測試

**檢查點**:
- [ ] 測試使用真實後端 (或 Mock Server)
- [ ] 測試資料清理
- [ ] 跨瀏覽器測試 (如需要)

### 4.4 手動測試

#### 功能測試
- [ ] 建立功能正常運作
- [ ] 列表功能正常運作
- [ ] 查詢功能正常運作
- [ ] 更新功能正常運作
- [ ] 刪除功能正常運作

#### UI/UX 測試
- [ ] 表單 UX 流暢
- [ ] 錯誤訊息清楚
- [ ] Loading 狀態正常
- [ ] 響應式設計正常
- [ ] 無障礙功能正常

#### 瀏覽器相容性
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile (iOS/Android)

---

## 5. 文件更新 (Documentation)

### 5.1 API 規格文件

**檔案路徑**: `docs/06_api_design_specification.md`

- [ ] API 端點文件更新
  ```markdown
  ### [METHOD] /api/v1/[endpoint]

  **描述**: [功能描述]

  **Request**:
  ```json
  {
    "field1": "value",
    "field2": 100
  }
  ```

  **Response**:
  ```json
  {
    "id": "uuid",
    "field1": "value",
    "field2": 100
  }
  ```
  ```
- [ ] OpenAPI/Swagger 文檔自動生成
- [ ] Postman Collection 更新 (如有)

### 5.2 CHANGELOG

**檔案路徑**: `docs/dev_logs/CHANGELOG.md`

- [ ] 新增變更記錄
  ```markdown
  ## [Unreleased]

  ### Added
  - [Feature] 新增 [功能名稱] API (#Issue編號)
    - POST /api/v1/[endpoint] - 建立
    - GET /api/v1/[endpoint] - 查詢
    - ...

  ### Changed
  - [Feature] 更新 [功能名稱] 的驗證邏輯

  ### Fixed
  - [Bug] 修復 [功能名稱] 的 XXX 問題
  ```

### 5.3 WBS 文件

**檔案路徑**: `docs/16_wbs_development_plan.md`

- [ ] 更新任務狀態
  ```markdown
  | 任務編號 | 任務名稱 | 狀態 | 完成度 | 完成日期 |
  |---------|---------|------|--------|---------|
  | X.Y.Z | [功能名稱] API | ✅ | 100% | YYYY-MM-DD |
  ```
- [ ] 更新工時記錄
- [ ] 更新進度百分比

---

## 6. 問題追蹤 (Issue Tracking)

### 發現的問題

| 問題編號 | 問題描述 | 嚴重性 | 狀態 | 解決日期 |
|---------|---------|--------|------|---------|
| #001 | [問題描述] | P0/P1/P2/P3 | ⬜ 未處理 | - |

### 待解決事項

- [ ] 待解決1
- [ ] 待解決2

---

## 7. 完成確認 (Completion Checklist)

### 7.1 所有檢查點完成

- [ ] 後端實作 (8項)
  - [ ] 資料庫 Model
  - [ ] Pydantic Schemas
  - [ ] Repository Layer
  - [ ] Use Case Layer
  - [ ] API Router
  - [ ] 單元測試
  - [ ] API 整合測試
  - [ ] 程式碼審查通過
- [ ] 前端實作 (5項)
  - [ ] TypeScript Types
  - [ ] API Client
  - [ ] React Hook
  - [ ] UI Components
  - [ ] Mock 資料
- [ ] 整合驗證 (4項)
  - [ ] 資料流驗證
  - [ ] 欄位對齊檢查
  - [ ] E2E 測試
  - [ ] 手動測試
- [ ] 文件更新 (3項)
  - [ ] API 規格文件
  - [ ] CHANGELOG
  - [ ] WBS 文件

### 7.2 測試覆蓋率達標

- [ ] 單元測試覆蓋率 > 80%
- [ ] API 測試全部通過
- [ ] E2E 測試全部通過

### 7.3 Code Review

- [ ] Code Review 已完成
- [ ] Review Comments 已處理
- [ ] 程式碼品質符合標準

### 7.4 最終驗證

- [ ] 前後端功能完全對齊
- [ ] 資料流完整無誤
- [ ] 所有測試通過
- [ ] 文件同步更新
- [ ] WBS 狀態正確

---

## 8. 簽核 (Sign-off)

**開發者**: [姓名] - 日期: YYYY-MM-DD
**審查者**: [姓名] - 日期: YYYY-MM-DD
**批准者**: [姓名] - 日期: YYYY-MM-DD

**最終狀態**: ✅ 已完成 / 🟡 部分完成 / ❌ 未完成

---

**參考文件**:
- [開發方法與任務追蹤標準](../development_methodology_and_tracking_standard.md)
- [功能對齊驗證模板](./feature_alignment_verification_template.md)
