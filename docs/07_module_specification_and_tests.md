# 模組規格與測試案例: 風險引擎

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-16`
**主要作者:** `Claude Code AI`
**狀態:** `待開發 (To Do)`

---

## 模組: `RiskEngineService`

**對應架構文件**: [05_architecture_and_design.md](./05_architecture_and_design.md)
**架構說明**: 此模組為 **Modular Monolith** 中的核心業務模組（位於 `backend/src/respira_ally/application/risk_engine/`），負責計算病患健康分數與風險分級。Phase 3 後可獨立為微服務。
**對應 BDD Feature**: `N/A` (系統內部邏輯)
**對應使用者故事**: `US-601`

---

### 規格 1: `calculate_health_score`

**描述 (Description)**: 根據病患近期的一系列健康指標，計算其綜合健康分數。此分數用於動態更新風險等級。

**函式簽名 (Python Type Hints)**:
```python
def calculate_health_score(
    adherence_7d: float,         # 7 日依從率 (0.0 - 1.0)
    water_avg_30d: float,        # 30 日平均飲水量 (ml)
    exercise_avg_30d: float,     # 30 日平均運動時長 (min)
    smoke_avg_7d: float,         # 7 日平均抽菸量 (支)
    latest_cat_score: int,       # 最新 CAT 問卷分數 (0 - 40)
    survey_risk_normalized: int, # 最新問卷正規化風險 (0 - 100)
    bmi: Optional[float] = None, # BMI 值 (若有身高體重)
    smoking_years: Optional[int] = None, # 吸菸年數 (若為吸菸者)
) -> int:
    """Calculates the patient's health score based on multiple factors."""
    ...
```

**核心公式** (更新版,考慮新健康指標):

**基礎公式**:
`S_base = 0.30×A₇ + 0.15×H₃₀ + 0.15×(100-N₃₀) + 0.15×(100-C) + 0.20×(100-R̂)`

**健康指標調整** (若資料可用):
- **BMI 調整**:
  - BMI < 18.5 (過輕): -5 分
  - BMI 18.5-24 (正常): 0 分
  - BMI 24-27 (過重): -3 分
  - BMI ≥ 27 (肥胖): -8 分
- **吸菸年數調整**:
  - smoking_years ≥ 20: -10 分
  - smoking_years 10-19: -5 分
  - smoking_years 1-9: -2 分
  - smoking_status = "NEVER": 0 分

**最終分數**:
`S_final = S_base + BMI_adjustment + Smoking_adjustment`
*(確保最終分數在 0-100 範圍內)*

*備註: A₇ 為依從率百分比 (0-100), H₃₀, N₃₀, C, R̂ 都是經過正規化到 0-100 區間的值。*

**契約式設計 (Design by Contract, DbC)**:
*   **前置條件 (Preconditions)**:
    1.  `adherence_7d` 必須在 `0.0` 到 `1.0` 之間。
    2.  所有 `avg` 輸入值必須 `≥ 0`。
    3.  `latest_cat_score` 必須在 `0` 到 `40` 之間。
    4.  `survey_risk_normalized` 必須在 `0` 到 `100` 之間。
*   **後置條件 (Postconditions)**:
    1.  返回的健康分數必須是一個 `0` 到 `100` 之間的整數。
*   **不變性 (Invariants)**:
    1.  權重總和 (`0.35 + 0.15 + 0.15 + 0.15 + 0.20`) 必須恆等於 `1.0`。

---

### 測試情境與案例 (Test Scenarios & Cases)

#### 情境 1: 正常路徑 - 健康狀況良好的病患

*   **測試案例 ID**: `TC-RiskEngine-001`
*   **描述**: 一個各項指標都表現良好的病患，應得到一個高的健康分數。
*   **輸入值 (假設已正規化)**:
    *   `A₇` (依從率): 100 (100%)
    *   `H₃₀` (飲水): 90
    *   `N₃₀` (運動): 85
    *   `C` (抽菸): 0
    *   `R̂` (問卷風險): 10
*   **預期計算**: `0.35*100 + 0.15*90 + 0.15*(100-0) + 0.15*(100-10) + 0.20*(100-85)` -> `35 + 13.5 + 15 + 13.5 + 1 = 78` (這裡公式似乎有誤，應為 `0.20*R̂` or `0.20*(100-R̂)`. 根據AC，分數越高越好，所以應為 `0.20×(100-R̂)`)
    * `S = 0.35*100 + 0.15*90 + 0.15*85 + 0.15*(100-0) + 0.20*(100-10) = 35 + 13.5 + 12.75 + 15 + 18 = 94.25` 
    * 根據`AGILE_DESIGN_DOCUMENT`的公式 `S = 0.35×A₇ + 0.15×H₃₀ + 0.15×(100-N₃₀) + 0.15×(100-C) + 0.20×(100-R̂)`，其中A7是依從率，H30是飲水，N30是運動，C是抽菸，R̂是問卷風險。 A, H, N, C 都是越大越好, R̂ 是越小越好。
    * 讓我們重新根據 `AGILE_DESIGN_DOCUMENT` 的公式 `S = 0.35×A₇ + 0.15×H₃₀ + 0.15×(100-N₃₀) + 0.15×(100-C) + 0.20×(100-R̂)`
    *   `A₇` (依從率): 100
    *   `H₃₀` (飲水): 90
    *   `N₃₀` (運動): 85
    *   `C` (抽菸): 0
    *   `R̂` (問卷風險): 10
    * `S = 0.35*100 + 0.15*90 + 0.15*(100-85) + 0.15*(100-0) + 0.20*(100-10)`
    * `S = 35 + 13.5 + 0.15*15 + 0.15*100 + 0.20*90 = 35 + 13.5 + 2.25 + 15 + 18 = 83.75`
*   **預期結果**: `round(83.75)` -> `84`。屬於 "Low" risk bucket (≥80)。

#### 情境 2: 正常路徑 - 健康狀況較差的病患

*   **測試案例 ID**: `TC-RiskEngine-002`
*   **描述**: 一個多項指標不佳的病患，應得到一個低的健康分數。
*   **輸入值 (假設已正規化)**:
    *   `A₇` (依從率): 30
    *   `H₃₀` (飲水): 40
    *   `N₃₀` (運動): 20
    *   `C` (抽菸): 50
    *   `R̂` (問卷風險): 70
*   **預期計算**: `S = 0.35*30 + 0.15*40 + 0.15*(100-20) + 0.15*(100-50) + 0.20*(100-70) = 10.5 + 6 + 12 + 7.5 + 6 = 42`
*   **預期結果**: `42`。屬於 "High" risk bucket (<60)。

#### 情境 3: 邊界情況 - 所有指標均為最差

*   **測試案例 ID**: `TC-RiskEngine-003`
*   **描述**: 測試分數的下限。
*   **輸入值**: `A₇=0, H₃₀=0, N₃₀=0, C=100, R̂=100`
*   **預期計算**: `S = 0.35*0 + 0.15*0 + 0.15*(100-0) + 0.15*(100-100) + 0.20*(100-100) = 0 + 0 + 15 + 0 + 0 = 15`
*   **預期結果**: `15`。

#### 情境 4: 邊界情況 - 所有指標均為最佳

*   **測試案例 ID**: `TC-RiskEngine-004`
*   **描述**: 測試分數的上限。
*   **輸入值**: `A₇=100, H₃₀=100, N₃₀=100, C=0, R̂=0`
*   **預期計算**: `S = 0.35*100 + 0.15*100 + 0.15*(100-100) + 0.15*(100-0) + 0.20*(100-0) = 35 + 15 + 0 + 15 + 20 = 85`
*   **預期結果**: `85`。
*   *Note: 根據公式，滿分似乎不是100，這是一個需要和產品經理確認的點。*

#### 情境 5: 無效輸入 (違反前置條件)

*   **測試案例 ID**: `TC-RiskEngine-005`
*   **描述**: 輸入的依從率為負數。
*   **測試步驟**: 呼叫 `calculate_health_score(adherence_7d=-0.5, ...)`
*   **預期結果**: 拋出 `ValueError` 或類似的例外，並提示 "adherence_7d must be between 0.0 and 1.0"。

#### 情境 6: 考慮新健康指標 - 肥胖且長期吸菸者

*   **測試案例 ID**: `TC-RiskEngine-006`
*   **描述**: 病患有肥胖問題 (BMI ≥ 27) 且長期吸菸 (≥20年),應額外扣分。
*   **輸入值**:
    *   基礎指標: `A₇=80, H₃₀=70, N₃₀=60, C=30, R̂=40`
    *   `bmi=29.5` (肥胖)
    *   `smoking_years=25` (長期吸菸)
*   **預期計算**:
    *   `S_base = 0.30*80 + 0.15*70 + 0.15*(100-60) + 0.15*(100-30) + 0.20*(100-40)`
    *   `S_base = 24 + 10.5 + 6 + 10.5 + 12 = 63`
    *   `BMI_adjustment = -8` (肥胖)
    *   `Smoking_adjustment = -10` (≥20年)
    *   `S_final = 63 - 8 - 10 = 45`
*   **預期結果**: `45`。屬於 "High" risk bucket (<60)。

---

## 模組: `KPICalculationService`

**對應架構文件**: [05_architecture_and_design.md - Section 5.3](./05_architecture_and_design.md#53-kpi-快取層與資料視圖設計)
**架構說明**: 此模組負責計算與刷新病患 KPI 快取數據,為前端提供高效能查詢。
**對應資料庫設計**: [DATABASE_SCHEMA_DESIGN.md - Section 4.5](./DATABASE_SCHEMA_DESIGN.md#45-patient_kpi_cache-kpi-快取表)

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
