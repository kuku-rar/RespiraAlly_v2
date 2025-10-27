# 模組規格與測試案例: 風險引擎

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-27`
**主要作者:** `Claude Code AI`
**狀態:** `開發中 (In Progress)`

---

## Phase-Sprint 開發階段映射

為確保文件術語一致性，本系統採用以下 Phase-Sprint 對應關係（詳見 [02_product_requirements_document.md](./02_product_requirements_document.md) Section 4.1）：

| Phase | 時程 | Sprint | 模組開發重點 |
|-------|------|--------|--------------|
| **Phase 0: 核心驗證** | Week 1-4 | Sprint 0-2 | 病患管理服務、KPI 計算服務 |
| **Phase 1: 增值功能** | Week 5-8 | Sprint 3-4 | 風險引擎服務、警示管理服務 |
| **Phase 2: AI 能力** | Week 9-12 | Sprint 5-6 | RAG 服務、語音處理服務 |
| **Phase 3: 優化上線** | Week 13-16 | Sprint 7-8 | 通知服務、監控服務 |

**當前進度**: Sprint 4 (Phase 1) - 風險引擎服務開發中

---

## 模組: `RiskEngineService`

**對應架構文件**: [05_architecture_and_design.md](./05_architecture_and_design.md)
**架構說明**: 此模組為 **Modular Monolith** 中的核心業務模組（位於 `backend/src/respira_ally/application/risk/`），負責計算病患健康分數與風險分級。Phase 3 後可獨立為微服務。
**對應 BDD Feature**: `N/A` (系統內部邏輯)
**對應使用者故事**: `US-601`

---

### 規格 1: `_classify_gold_group` (GOLD ABE 風險分級)

**描述 (Description)**: 根據 GOLD ABE 臨床指引（GOLD 2011）對 COPD 病患進行風險分級。此方法為風險評估的核心領域邏輯，基於病患症狀嚴重程度（CAT 問卷和 mMRC 呼吸困難量表）進行分類。

**臨床背景**: GOLD ABE 分類是國際公認的 COPD 風險評估標準，用於指導治療決策和監測病情發展。

**函式簽名 (Python Type Hints)**:
```python
def _classify_gold_group(
    self,
    cat_score: int,    # CAT 問卷分數 (0-40)
    mmrc_grade: int,   # mMRC 呼吸困難等級 (0-4)
) -> GoldGroup:
    """
    Classify patient into GOLD ABE group based on symptom severity.

    Returns:
        GoldGroup: 'A' (low risk) | 'B' (medium risk) | 'E' (high risk)
    """
    ...
```

**GOLD ABE 分類算法** (GOLD 2011 臨床指引):

```
症狀閾值定義:
- high_symptoms_cat = (CAT 分數 >= 10)
- high_symptoms_mmrc = (mMRC 等級 >= 2)

分類規則（無特殊情況，清晰的三分支邏輯）:
┌─────────────────────────┬─────────────────────┬──────────┬────────────┐
│ CAT 症狀                │ mMRC 症狀           │ GOLD 組別│ 風險等級   │
├─────────────────────────┼─────────────────────┼──────────┼────────────┤
│ CAT ≥ 10 (高症狀)       │ mMRC ≥ 2 (高症狀)   │ Group E  │ High (高)  │
│ CAT ≥ 10 (高症狀)       │ mMRC < 2 (低症狀)   │ Group B  │ Medium (中)│
│ CAT < 10 (低症狀)       │ mMRC ≥ 2 (高症狀)   │ Group B  │ Medium (中)│
│ CAT < 10 (低症狀)       │ mMRC < 2 (低症狀)   │ Group A  │ Low (低)   │
└─────────────────────────┴─────────────────────┴──────────┴────────────┘

簡化邏輯表達:
IF (CAT ≥ 10) AND (mMRC ≥ 2) THEN Group E  // 雙高 → 高風險
ELSE IF (CAT ≥ 10) OR (mMRC ≥ 2) THEN Group B  // 單高 → 中風險
ELSE Group A  // 雙低 → 低風險
```

**與 Legacy 風險評分的映射** (ADR-014 混合策略):
- Group A → risk_score=25, risk_level='low'
- Group B → risk_score=50, risk_level='medium'
- Group E → risk_score=75, risk_level='high'

*註：Legacy 的 risk_score (0-100) 和 risk_level 欄位保留以維持向後兼容性，但 GOLD 組別為主要分類標準。*

**契約式設計 (Design by Contract, DbC)**:
*   **前置條件 (Preconditions)**:
    1.  `cat_score` 必須在 `0` 到 `40` 之間（CAT 問卷標準範圍）。
    2.  `mmrc_grade` 必須在 `0` 到 `4` 之間（mMRC 量表標準範圍）。
*   **後置條件 (Postconditions)**:
    1.  返回值必須為 `'A'`, `'B'`, 或 `'E'` 之一。
    2.  分類結果必須符合 GOLD 2011 臨床指引規則。
*   **不變性 (Invariants)**:
    1.  相同的輸入必須產生相同的輸出（純函數，無副作用）。
    2.  症狀閾值恆定：CAT 閾值=10, mMRC 閾值=2。

---

### 測試情境與案例 (Test Scenarios & Cases)

#### 情境 1: 高風險病患 - 雙高症狀 (Group E)

*   **測試案例 ID**: `TC-GOLD-001`
*   **描述**: CAT 和 mMRC 皆達到高症狀閾值，應分類為 Group E（高風險）。
*   **輸入值**:
    *   `cat_score = 18` (≥10, 高症狀)
    *   `mmrc_grade = 3` (≥2, 高症狀)
*   **預期邏輯**:
    ```
    high_symptoms_cat = (18 >= 10) = True
    high_symptoms_mmrc = (3 >= 2) = True
    → Both high → Group E
    ```
*   **預期結果**: `gold_group = 'E'`
*   **對應 Legacy 映射**: `risk_score = 75`, `risk_level = 'high'`

#### 情境 2: 中風險病患 - CAT 高症狀，mMRC 低症狀 (Group B)

*   **測試案例 ID**: `TC-GOLD-002`
*   **描述**: 僅 CAT 達到高症狀閾值，mMRC 低於閾值，應分類為 Group B（中風險）。
*   **輸入值**:
    *   `cat_score = 12` (≥10, 高症狀)
    *   `mmrc_grade = 1` (<2, 低症狀)
*   **預期邏輯**:
    ```
    high_symptoms_cat = (12 >= 10) = True
    high_symptoms_mmrc = (1 >= 2) = False
    → One high → Group B
    ```
*   **預期結果**: `gold_group = 'B'`
*   **對應 Legacy 映射**: `risk_score = 50`, `risk_level = 'medium'`

#### 情境 3: 中風險病患 - mMRC 高症狀，CAT 低症狀 (Group B)

*   **測試案例 ID**: `TC-GOLD-003`
*   **描述**: 僅 mMRC 達到高症狀閾值，CAT 低於閾值，應分類為 Group B（中風險）。
*   **輸入值**:
    *   `cat_score = 8` (<10, 低症狀)
    *   `mmrc_grade = 3` (≥2, 高症狀)
*   **預期邏輯**:
    ```
    high_symptoms_cat = (8 >= 10) = False
    high_symptoms_mmrc = (3 >= 2) = True
    → One high → Group B
    ```
*   **預期結果**: `gold_group = 'B'`
*   **對應 Legacy 映射**: `risk_score = 50`, `risk_level = 'medium'`

#### 情境 4: 低風險病患 - 雙低症狀 (Group A)

*   **測試案例 ID**: `TC-GOLD-004`
*   **描述**: CAT 和 mMRC 皆低於高症狀閾值，應分類為 Group A（低風險）。
*   **輸入值**:
    *   `cat_score = 5` (<10, 低症狀)
    *   `mmrc_grade = 1` (<2, 低症狀)
*   **預期邏輯**:
    ```
    high_symptoms_cat = (5 >= 10) = False
    high_symptoms_mmrc = (1 >= 2) = False
    → Both low → Group A
    ```
*   **預期結果**: `gold_group = 'A'`
*   **對應 Legacy 映射**: `risk_score = 25`, `risk_level = 'low'`

#### 情境 5: 邊界測試 - 閾值臨界點 (Group E)

*   **測試案例 ID**: `TC-GOLD-005`
*   **描述**: CAT 和 mMRC 皆剛好達到閾值，應分類為 Group E。
*   **輸入值**:
    *   `cat_score = 10` (≥10, 邊界值)
    *   `mmrc_grade = 2` (≥2, 邊界值)
*   **預期邏輯**:
    ```
    high_symptoms_cat = (10 >= 10) = True  // 包含等於
    high_symptoms_mmrc = (2 >= 2) = True   // 包含等於
    → Both high → Group E
    ```
*   **預期結果**: `gold_group = 'E'`
*   **臨床意義**: 閾值包含性（≥ 而非 >）符合 GOLD 2011 指引。

#### 情境 6: 邊界測試 - 閾值下界 (Group A)

*   **測試案例 ID**: `TC-GOLD-006`
*   **描述**: CAT 和 mMRC 皆剛好低於閾值，應分類為 Group A。
*   **輸入值**:
    *   `cat_score = 9` (<10, 邊界值)
    *   `mmrc_grade = 1` (<2, 邊界值)
*   **預期邏輯**:
    ```
    high_symptoms_cat = (9 >= 10) = False
    high_symptoms_mmrc = (1 >= 2) = False
    → Both low → Group A
    ```
*   **預期結果**: `gold_group = 'A'`

#### 情境 7: 極端值測試 - 最嚴重症狀 (Group E)

*   **測試案例 ID**: `TC-GOLD-007`
*   **描述**: CAT 和 mMRC 達到最大值，應分類為 Group E。
*   **輸入值**:
    *   `cat_score = 40` (CAT 問卷最大值)
    *   `mmrc_grade = 4` (mMRC 量表最大值)
*   **預期結果**: `gold_group = 'E'`

#### 情境 8: 極端值測試 - 無症狀 (Group A)

*   **測試案例 ID**: `TC-GOLD-008`
*   **描述**: CAT 和 mMRC 達到最小值，應分類為 Group A。
*   **輸入值**:
    *   `cat_score = 0` (CAT 問卷最小值)
    *   `mmrc_grade = 0` (mMRC 量表最小值)
*   **預期結果**: `gold_group = 'A'`

#### 情境 9: 無效輸入 - CAT 超出範圍

*   **測試案例 ID**: `TC-GOLD-009`
*   **描述**: CAT 分數超出有效範圍 (0-40)，應拋出驗證錯誤。
*   **測試步驟**: 呼叫 `_classify_gold_group(cat_score=45, mmrc_grade=2)`
*   **預期結果**: 拋出 `ValueError` 或 `ValidationError`，並提示 "cat_score must be between 0 and 40"。

#### 情境 10: 無效輸入 - mMRC 超出範圍

*   **測試案例 ID**: `TC-GOLD-010`
*   **描述**: mMRC 等級超出有效範圍 (0-4)，應拋出驗證錯誤。
*   **測試步驟**: 呼叫 `_classify_gold_group(cat_score=15, mmrc_grade=5)`
*   **預期結果**: 拋出 `ValueError` 或 `ValidationError`，並提示 "mmrc_grade must be between 0 and 4"。

---

## 模組: `KPICalculationService`

**對應架構文件**: [05_architecture_and_design.md - Section 5.3](./05_architecture_and_design.md#53-kpi-快取層與資料視圖設計)
**架構說明**: 此模組負責計算與刷新病患 KPI 快取數據,為前端提供高效能查詢。
**對應資料庫設計**: [database/schema_design_v1.0.md - Section 4.5](./database/schema_design_v1.0.md#45-patient_kpi_cache-kpi-快取表)

---

### 規格 2: `refresh_patient_kpi_cache`

**描述**: 刷新指定病患或所有病患的 KPI 快取數據 (對應資料庫存儲過程)。

**函式簽名**:
```python
async def refresh_patient_kpi_cache(
    db: AsyncSession,
    patient_id: Optional[UUID] = None,
) -> RefreshResult:
    """
    刷新病患 KPI 快取。

    Args:
        db: 資料庫會話
        patient_id: 指定病患 ID (若為 None 則刷新所有病患)

    Returns:
        RefreshResult 包含:
            - refreshed_count: 刷新的病患數量
            - duration_ms: 執行時間 (毫秒)
    """
    ...
```

**契約式設計**:
*   **前置條件**:
    1. `db` 必須為有效的資料庫會話
    2. 若提供 `patient_id`,該 ID 必須存在於 `patient_profiles` 表
*   **後置條件**:
    1. `patient_kpi_cache.last_calculated_at` 已更新為當前時間
    2. 所有計算型 KPI (依從率、平均值等) 已更新
*   **副作用**:
    1. 更新資料庫 `patient_kpi_cache` 表
    2. 可能觸發相關索引更新

---

### 測試情境與案例

#### 情境 1: 刷新單一病患 KPI

*   **測試案例 ID**: `TC-KPI-001`
*   **描述**: 刷新特定病患的 KPI 快取。
*   **前置條件**:
    *   病患 `patient-A` 存在
    *   病患 `patient-A` 有 10 筆 daily_logs (近 7 天: 7 筆, 近 30 天: 10 筆)
    *   7 天內用藥 5 次
*   **測試步驟**: 呼叫 `refresh_patient_kpi_cache(db, patient_id="patient-A")`
*   **預期結果**:
    *   `refreshed_count = 1`
    *   `patient_kpi_cache.adherence_rate_7d = 71` (5/7 ≈ 71%)
    *   `patient_kpi_cache.last_calculated_at` 已更新
    *   執行時間 < 100ms

#### 情境 2: 批量刷新所有病患 KPI

*   **測試案例 ID**: `TC-KPI-002`
*   **描述**: 刷新所有病患的 KPI 快取 (定期排程任務)。
*   **前置條件**: 系統中有 100 位病患
*   **測試步驟**: 呼叫 `refresh_patient_kpi_cache(db, patient_id=None)`
*   **預期結果**:
    *   `refreshed_count = 100`
    *   所有病患的 `last_calculated_at` 已更新
    *   執行時間 < 10 秒 (平均 100ms/病患)

#### 情境 3: 刷新不存在的病患

*   **測試案例 ID**: `TC-KPI-003`
*   **描述**: 嘗試刷新不存在的病患 ID。
*   **測試步驟**: 呼叫 `refresh_patient_kpi_cache(db, patient_id="nonexistent-id")`
*   **預期結果**: 拋出 `PatientNotFoundError`

---

### 規格 3: `calculate_bmi`

**描述**: 根據身高體重計算 BMI 並分級。

**函式簽名**:
```python
def calculate_bmi(
    height_cm: int,
    weight_kg: float,
) -> BMIResult:
    """
    計算 BMI 與分級。

    Returns:
        BMIResult(
            bmi: float,  # 計算結果 (保留1位小數)
            category: str  # UNDERWEIGHT/NORMAL/OVERWEIGHT/OBESE
        )
    """
    ...
```

**測試案例**:

*   **TC-BMI-001** (正常): `height_cm=170, weight_kg=65` → `BMI=22.5, category=NORMAL`
*   **TC-BMI-002** (過輕): `height_cm=175, weight_kg=55` → `BMI=18.0, category=UNDERWEIGHT`
*   **TC-BMI-003** (肥胖): `height_cm=160, weight_kg=75` → `BMI=29.3, category=OBESE`
*   **TC-BMI-004** (邊界): `height_cm=170, weight_kg=69.3` → `BMI=24.0, category=NORMAL` (邊界值)
