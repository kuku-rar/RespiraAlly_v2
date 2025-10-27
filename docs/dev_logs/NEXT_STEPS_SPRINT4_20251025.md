# Sprint 4 下一步行動計畫 (Next Steps Action Plan)

**文件日期**: 2025-10-25 23:20
**當前進度**: Sprint 4 Phase 1.6 完成 (20.5h / 104h, 20%)
**目標**: 完成 Sprint 4 風險引擎 & 預警系統

---

## 📊 當前狀態摘要

### ✅ 已完成 (Phase 1.0 - 1.6)
- [x] Frontend Hybrid Strategy (3.5h)
- [x] Backend GOLD ABE Engine (5h)
- [x] RBAC Extension (4.0h)
- [x] Critical Bug Fixes (1.0h)
- [x] Dual-Schema Architecture & Migration 005 Preparation (2.0h)
- [x] Taiwan Localization Test Data (2.0h)
- [x] **Dashboard 風險篩選快速驗證 (3.0h)**

### 🎯 Sprint 4 剩餘工時
**總工時**: 104h
**已完成**: 20.5h (19.7%)
**剩餘**: 83.5h (80.3%)

---

## 🚀 優先級 1: 立即可執行 (P0)

### Task 1: Dashboard 手動 UI 測試 [15min] ⭐ 最優先

**目標**: 驗證 Phase 1.6 實作的風險篩選功能是否正常運作

**前置條件**:
- ✅ Backend API 運行中 (port 8000)
- ✅ Frontend Dev 運行中 (port 3000)
- ✅ 測試數據已載入 (50 patients)

**測試步驟**:

#### 1.1 登入與基本顯示測試
```
URL: http://localhost:3000/login
帳號: therapist1@respira-ally.com
密碼: SecurePass123!

驗證項目:
☐ 登入成功
☐ 導航至 /patients 頁面
☐ 患者列表正確顯示 50 位患者
☐ 每位患者顯示風險等級 badge (emoji + 標籤 + 顏色)
```

#### 1.2 風險等級篩選測試
```
測試案例 1: 篩選高風險患者
1. 點擊「展開篩選 ▼」
2. 風險等級下拉選單選擇「高風險」
3. 點擊「套用篩選」
預期結果: 顯示 2-3 位患者，所有 badge 為橙色「🔶 高風險」

測試案例 2: 篩選緊急患者
1. 風險等級選擇「緊急」
2. 點擊「套用篩選」
預期結果: 顯示 1-2 位患者，所有 badge 為紅色「🚨 緊急」

測試案例 3: 重置篩選
1. 點擊「重置篩選」
預期結果: 顯示全部 50 位患者，排序回到「姓名（A-Z）」
```

#### 1.3 風險等級排序測試
```
1. 排序下拉選單選擇「風險等級（高→低）」
預期結果:
☐ 緊急患者排在最前面
☐ 高風險患者次之
☐ 中風險患者再次
☐ 低風險患者最後
```

#### 1.4 測試結果記錄
```
完成後更新:
- docs/test_reports/sprint4-dashboard-risk-filter-test.md
  - 更新「實作驗證 Checklist」區段
  - 新增「實際測試結果」區段
  - 附上截圖（可選）
```

**完成條件**:
- [ ] 所有測試案例通過
- [ ] 測試報告更新並提交
- [ ] 如有 bug，記錄於 GitHub Issues

**預計時間**: 15-30 分鐘

---

## 🎯 優先級 2: 短期規劃 (P1)

### Task 2: GOLD 2011 ABE 分類標準研究 [1h]

**目標**: 深入理解 GOLD ABE 分類系統，為完整實作奠定基礎

**研究重點**:

#### 2.1 GOLD ABE 分類標準
```
參考文獻:
- GOLD 2011 Global Strategy for Diagnosis, Management and Prevention of COPD
- GOLD ABE Classification System

關鍵問題:
1. ABE 三組的定義與判斷標準是什麼？
   - Group A: Low risk, fewer symptoms
   - Group B: Low risk, more symptoms
   - Group E: Exacerbation history

2. 需要哪些臨床數據？
   - CAT (COPD Assessment Test) score: 0-40
   - mMRC (Modified Medical Research Council) grade: 0-4
   - Exacerbation history (過去 12 個月)
   - Hospitalization history
   - FEV1 (Forced Expiratory Volume) - 選填

3. 分類演算法邏輯？
   決策樹 / 規則引擎設計
```

#### 2.2 與現有實作的差異分析
```
當前簡化版 (Phase 1.6):
- 僅基於 exacerbation_count 和 hospitalization_count
- 風險等級: LOW/MEDIUM/HIGH/CRITICAL

完整 GOLD ABE:
- 整合 CAT score + mMRC grade + exacerbation history
- 分組: A/B/E
- 更精確的風險分層

差距分析:
☐ 需新增 CAT 問卷數據收集
☐ 需新增 mMRC 評分數據收集
☐ 需設計 GOLD ABE 計算引擎
☐ 需更新 Frontend UI（顯示 ABE 分組）
```

#### 2.3 技術實作方案草案
```
Backend:
- 擴展 RiskAssessmentModel（已有 gold_group 欄位）
- 新增 GoldAbeClassificationService
- 實作決策樹邏輯

Frontend:
- 更新 risk.ts 工具函數
- 新增 GOLD ABE badge 顯示
- 支持雙模式（簡化 + GOLD ABE）
```

**交付物**:
- [ ] 研究筆記文檔 (Markdown)
- [ ] GOLD ABE 分類演算法偽代碼
- [ ] 技術實作方案草案

**完成條件**:
- [ ] 完整理解 GOLD ABE 分類標準
- [ ] 設計出實作方案草案
- [ ] 識別技術風險與挑戰

**預計時間**: 1 小時

---

### Task 3: 設計完整 GOLD ABE 引擎架構 [1h]

**目標**: 設計可擴展、可維護的 GOLD ABE 分類引擎

**設計範疇**:

#### 3.1 系統架構設計
```
┌─────────────────────────────────────────────────┐
│  Frontend (Dashboard & LIFF)                    │
│  - GOLD ABE 分組顯示                            │
│  - CAT 問卷表單                                 │
│  - mMRC 評分表單                                │
└───────────────────┬─────────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────────┐
│  Application Layer                              │
│  - GoldAbeAssessmentUseCase                     │
│  - RiskCalculationUseCase                       │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│  Domain Layer                                   │
│  - GoldAbeClassificationEngine ⭐ 核心邏輯       │
│  - RiskAssessment Aggregate                     │
│  - Domain Events                                │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│  Infrastructure Layer                           │
│  - RiskAssessmentRepository                     │
│  - ExacerbationRepository                       │
└─────────────────────────────────────────────────┘
```

#### 3.2 核心類別設計
```python
# Domain Layer
class GoldAbeClassificationEngine:
    """
    GOLD ABE 分類引擎

    Input:
    - cat_score: int (0-40)
    - mmrc_grade: int (0-4)
    - exacerbation_count_12m: int
    - hospitalization_count_12m: int

    Output:
    - gold_group: Literal['A', 'B', 'E']
    - risk_score: int (0-100)
    - risk_level: Literal['low', 'medium', 'high', 'critical']
    """

    def classify(
        self,
        cat_score: int,
        mmrc_grade: int,
        exacerbation_count: int,
        hospitalization_count: int
    ) -> GoldAbeClassification:
        # Decision tree logic
        pass

class RiskAssessment(AggregateRoot):
    """風險評估聚合根"""
    assessment_id: UUID
    patient_id: UUID
    gold_group: GoldGroup  # A, B, E
    cat_score: int
    mmrc_grade: int
    risk_score: int
    risk_level: RiskLevel
    assessed_at: datetime
```

#### 3.3 API 設計
```
POST /api/v1/risk-assessments/
Request Body:
{
  "patient_id": "uuid",
  "cat_score": 15,
  "mmrc_grade": 2,
  "exacerbation_count_12m": 1,
  "hospitalization_count_12m": 0
}

Response:
{
  "assessment_id": "uuid",
  "gold_group": "B",
  "risk_score": 55,
  "risk_level": "medium",
  "assessed_at": "2025-10-25T23:00:00Z"
}

GET /api/v1/patients/{patient_id}/risk-assessments/latest
Response:
{
  "assessment_id": "uuid",
  "gold_group": "E",
  "risk_score": 78,
  "risk_level": "high",
  "cat_score": 25,
  "mmrc_grade": 3,
  "exacerbation_count_12m": 2,
  "hospitalization_count_12m": 1,
  "assessed_at": "2025-10-25T22:00:00Z"
}
```

#### 3.4 Database Schema 驗證
```sql
-- 驗證 risk_assessments 表格欄位是否足夠
-- 已有欄位 (Migration 005):
-- - gold_group (GOLD ABE 分組)
-- - cat_score
-- - mmrc_grade
-- - exacerbation_count_12m
-- - hospitalization_count_12m
-- - risk_score
-- - risk_level

-- 確認無需額外 migration
```

**交付物**:
- [ ] 系統架構圖 (Mermaid)
- [ ] 核心類別 UML 設計
- [ ] API Specification (OpenAPI format)
- [ ] ADR-017: GOLD ABE Engine Design Decision

**完成條件**:
- [ ] 架構設計完整且清晰
- [ ] 符合 Clean Architecture 原則
- [ ] 考慮向後兼容性（與簡化版並存）

**預計時間**: 1 小時

---

## 🎯 優先級 3: 中期開發 (P1-P2)

### Task 4: Exacerbation Management API [12h]

**目標**: 實作急性惡化事件管理的完整 CRUD API

**前置條件**:
- ✅ Migration 005 已執行 (exacerbations 表格已建立)
- ✅ ExacerbationModel 已定義
- ✅ RBAC 授權系統已就緒

**開發範疇**:

#### 4.1 Schema 設計 [1h]
```python
# respira_ally/core/schemas/exacerbation.py

class ExacerbationBase(BaseModel):
    onset_date: date
    severity: ExacerbationSeverity  # MILD, MODERATE, SEVERE
    required_hospitalization: bool
    hospitalization_days: Optional[int] = None
    treatment_notes: Optional[str] = None
    resolved_date: Optional[date] = None

class ExacerbationCreate(ExacerbationBase):
    patient_id: UUID

class ExacerbationResponse(ExacerbationBase):
    exacerbation_id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

class ExacerbationListResponse(BaseModel):
    items: List[ExacerbationResponse]
    total: int
    page: int
    page_size: int
```

#### 4.2 Repository 實作 [2h]
```python
# respira_ally/infrastructure/database/repositories/exacerbation_repository.py

class ExacerbationRepository:
    async def create(self, exacerbation: ExacerbationCreate) -> ExacerbationModel
    async def get_by_id(self, exacerbation_id: UUID) -> Optional[ExacerbationModel]
    async def get_by_patient_id(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ExacerbationModel], int]
    async def update(self, exacerbation_id: UUID, data: dict) -> ExacerbationModel
    async def delete(self, exacerbation_id: UUID) -> None
```

#### 4.3 API Endpoints [4h]
```python
# respira_ally/api/v1/routers/exacerbation.py

POST   /api/v1/exacerbations/           # 創建急性惡化記錄（治療師）
GET    /api/v1/exacerbations/{id}       # 查詢單一記錄
GET    /api/v1/patients/{id}/exacerbations/  # 查詢患者的急性惡化歷史
PUT    /api/v1/exacerbations/{id}       # 更新記錄（治療師）
DELETE /api/v1/exacerbations/{id}       # 刪除記錄（治療師/管理員）
```

#### 4.4 Authorization Rules [1h]
```
THERAPIST:
- 可創建/查看/更新/刪除自己管理患者的記錄
- 不可操作其他治療師的患者記錄

PATIENT:
- 只可查看自己的記錄
- 不可創建/更新/刪除

SUPERVISOR/ADMIN:
- 可查看所有記錄
- 可創建/更新/刪除任何記錄
```

#### 4.5 Integration Tests [2h]
```python
# tests/integration/test_exacerbation_api.py

test_create_exacerbation_success()
test_create_exacerbation_unauthorized()
test_get_exacerbation_by_id()
test_get_patient_exacerbations_list()
test_update_exacerbation()
test_delete_exacerbation()
test_trigger_updates_patient_summary()  # 驗證 trigger function
```

#### 4.6 Documentation [1h]
- API 文檔更新（OpenAPI schema）
- 使用範例（curl commands）
- Postman Collection 更新

**完成條件**:
- [ ] 所有 CRUD endpoints 實作完成
- [ ] Integration tests 通過率 ≥ 90%
- [ ] API 文檔完整
- [ ] Trigger function 正確運作（自動更新 patient_profiles）

**預計時間**: 12 小時

---

### Task 5: Risk Assessment Engine - 完整實作 [16h]

**目標**: 實作基於 GOLD ABE 的完整風險評估引擎

**開發範疇**:

#### 5.1 GOLD ABE Classification Engine [6h]
```
- Domain Service: GoldAbeClassificationEngine
- 實作決策樹邏輯
- 單元測試（覆蓋所有邊界情況）
- 整合測試（端到端分類流程）
```

#### 5.2 Risk Assessment API [4h]
```
POST /api/v1/risk-assessments/
GET  /api/v1/patients/{id}/risk-assessments/latest
GET  /api/v1/patients/{id}/risk-assessments/history
```

#### 5.3 Automatic Trigger Integration [2h]
```
- Survey 完成 → 觸發風險評估
- DailyLog 提交 → 更新風險趨勢
- Exacerbation 記錄 → 重新評估
```

#### 5.4 Frontend Integration [3h]
```
- 更新 risk.ts（支持 GOLD ABE）
- PatientTable 顯示 GOLD 分組
- 風險詳情頁面（顯示計算明細）
```

#### 5.5 Testing & Documentation [1h]

**完成條件**:
- [ ] GOLD ABE 分類引擎正確運作
- [ ] 自動觸發機制測試通過
- [ ] Frontend 正確顯示 GOLD 分組
- [ ] 單元測試覆蓋率 ≥ 80%

**預計時間**: 16 小時

---

### Task 6: Alert System - 預警規則引擎 [12h]

**目標**: 實作基於規則的異常偵測與預警系統

**開發範疇**:

#### 6.1 Alert Rules Engine [4h]
```python
# Clinical Alert Rules
1. High-risk patient with worsening symptoms
2. Exacerbation frequency increasing
3. Medication non-compliance (< 70% adherence)
4. SpO2 below threshold (< 90%)
5. Rapid weight gain/loss
6. Prolonged inactivity
7. Smoking relapse
```

#### 6.2 Alert API [3h]
```
GET  /api/v1/alerts/?status=ACTIVE           # 查詢活動預警
POST /api/v1/alerts/{id}/acknowledge         # 確認預警
POST /api/v1/alerts/{id}/resolve             # 處理完成
GET  /api/v1/patients/{id}/alerts/           # 患者預警歷史
```

#### 6.3 Alert Notification Integration [3h]
```
- Email 通知（治療師）
- LINE Push Message（緊急預警）
- Dashboard 實時更新
```

#### 6.4 Testing & Documentation [2h]

**完成條件**:
- [ ] 至少 5 個臨床規則實作
- [ ] Alert 自動觸發機制測試通過
- [ ] 通知系統整合完成
- [ ] Dashboard 預警中心 UI 完成

**預計時間**: 12 小時

---

## 📊 工時預估總覽

| 優先級 | 任務 | 工時 | 累計 | 依賴關係 |
|--------|------|------|------|----------|
| P0 | Dashboard 手動 UI 測試 | 0.25h | 0.25h | - |
| P1 | GOLD ABE 標準研究 | 1h | 1.25h | - |
| P1 | GOLD ABE 引擎架構設計 | 1h | 2.25h | Task 2 |
| P1 | Exacerbation Management API | 12h | 14.25h | Migration 005 ✅ |
| P2 | Risk Assessment Engine | 16h | 30.25h | Task 3 |
| P2 | Alert System | 12h | 42.25h | Task 4, 5 |

**總計**: 42.25h (不含後續優化與測試)

**Sprint 4 剩餘工時**: 83.5h
**本計畫覆蓋率**: 50.6%

---

## 🎯 里程碑設定

### Milestone 1: Quick Validation Complete (當前位置) ✅
- 完成日期: 2025-10-25
- 交付物: 簡化風險計算 + Dashboard 篩選功能

### Milestone 2: GOLD ABE Research & Design
- 目標日期: +2 days
- 交付物: GOLD ABE 完整設計文檔 + ADR

### Milestone 3: Exacerbation API Complete
- 目標日期: +5 days
- 交付物: 完整 CRUD API + Integration Tests

### Milestone 4: Risk Assessment Engine Complete
- 目標日期: +8 days
- 交付物: GOLD ABE 分類引擎 + Frontend 整合

### Milestone 5: Alert System Complete
- 目標日期: +10 days
- 交付物: 預警規則引擎 + Dashboard 預警中心

---

## 📋 檢核清單 (Checklist)

### 立即行動（今日/明日）
- [ ] 執行 Dashboard 手動 UI 測試
- [ ] 更新測試報告
- [ ] 研究 GOLD 2011 ABE 分類標準

### 短期目標（本週）
- [ ] 完成 GOLD ABE 引擎設計
- [ ] 開始 Exacerbation API 開發
- [ ] 建立 ADR-017

### 中期目標（下週）
- [ ] Exacerbation API 完成並測試通過
- [ ] Risk Assessment Engine 開發啟動

---

## 🔗 參考資料

### 技術文件
- WBS: `docs/16-1_wbs_development_plan_sprint4-8.md`
- 測試報告: `docs/test_reports/sprint4-dashboard-risk-filter-test.md`
- Migration 005: `backend/alembic/versions/005_create_risk_engine_tables.sql`

### ADR 文件
- ADR-013: GOLD 2011 ABE Classification 採用決策
- ADR-014: Hybrid 向後兼容策略
- ADR-016: Migration 005 範圍定義
- ADR-017: GOLD ABE Engine Design (待建立)

### API 文檔
- OpenAPI Spec: `backend/docs/openapi.yaml` (待更新)
- Postman Collection: `backend/docs/postman/` (待更新)

---

## 💡 注意事項

### 技術風險
1. **GOLD ABE 分類複雜度**: 決策樹邏輯可能比預期複雜
2. **資料完整性**: CAT/mMRC 數據可能不完整，需考慮 fallback 邏輯
3. **效能問題**: 風險計算若頻繁觸發，需考慮快取策略

### 開發原則
- ✅ **漸進式開發**: 保持簡化版與完整版並存
- ✅ **向後兼容**: 新功能不影響現有系統
- ✅ **測試驅動**: 先寫測試，確保品質
- ✅ **文檔同步**: 代碼與文檔同時更新

### 品質要求
- 單元測試覆蓋率: ≥ 80%
- Integration 測試通過率: ≥ 90%
- API 回應時間: < 200ms (P95)
- 代碼 Review: 所有 PR 需經過審核

---

**最後更新**: 2025-10-25 23:20
**下次更新**: 完成 Task 1 後
