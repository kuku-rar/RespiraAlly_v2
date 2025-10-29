# 架構文件一致性分析報告

**文件版本**: v1.0
**分析日期**: 2025-10-28
**分析範圍**:
- `/docs/09_module_dependency_analysis.md`
- `/docs/10_class_relationships_and_module_design.md`
**對比目標**: 後端程式碼 (backend/) 與前端程式碼 (frontend/dashboard/)

---

## 執行摘要 (Executive Summary)

### 整體評估

| 評估項目 | 狀態 | 嚴重程度 |
|---------|------|---------|
| Repository Pattern 實作 | ✅ 符合 | - |
| Application Services 實作 | ✅ 符合 | - |
| Domain Services (Risk) 實作 | ✅ 符合 | - |
| DailyLog Entity 實作 | ✅ 符合 | - |
| **Patient Entity 實作** | ❌ **嚴重不符** | 🔴 **高** |
| **Value Objects 實作** | ❌ **完全缺失** | 🔴 **高** |
| **DIP (依賴反轉原則)** | ❌ **部分違反** | 🟡 **中** |
| 類別命名一致性 | ⚠️ 部分不符 | 🟢 低 |
| 前端型別定義 | ✅ 符合 | - |

### 關鍵發現

**🔴 嚴重問題**:
1. **Patient Entity 幾乎是空檔案** - 文件描述完整的 Domain Entity，但實際只有1行程式碼
2. **所有 Value Objects 未實作** - BMI、MedicalHistory、SmokingHistory 都是空檔案
3. **違反 DDD 原則** - 業務邏輯散落在 Application Service 而非 Domain Layer

**🟡 中等問題**:
4. **違反 Dependency Inversion Principle** - Domain Layer 的 Repository 介面引用了 Infrastructure Layer 的 ORM Model
5. **類別命名不一致** - 文件稱 `RiskEngine`，實際是 `RiskAssessmentService`

**🟢 正常部分**:
- Repository Pattern 正確實作 ✅
- Application Services 正確使用 DI ✅
- Risk Assessment 使用 GOLD ABE 分類 ✅
- 前端型別定義與後端對齊 ✅

---

## 詳細分析

## 1. Domain Layer (領域層) 分析

### 1.1 Domain Entities (領域實體)

#### ✅ DailyLog Entity - **完全符合**

**文件描述** (10_class_relationships.md, 行 392-572):
```python
@dataclass
class DailyLog:
    patient_id: UUID
    log_date: date
    medication_taken: bool | None = None
    # ... 業務邏輯方法
    def is_medication_adherent(self) -> bool:
        ...
```

**實際程式碼** (`backend/src/respira_ally/domain/entities/daily_log.py`):
```python
@dataclass
class DailyLog:
    patient_id: UUID
    log_date: date
    medication_taken: bool | None = None
    # ... 完整實作，包含所有業務邏輯方法
    def is_medication_adherent(self) -> bool:
        return self.medication_taken if self.medication_taken is not None else False
```

**評估**: ✅ **完全符合** - 甚至包含 Linus Torvalds 引言註解

---

#### ❌ Patient Entity - **嚴重不符**

**文件描述** (10_class_relationships.md, 行 1422-1595):
```python
@dataclass
class Patient:
    """Patient Aggregate Root"""
    user_id: UUID
    name: str
    birth_date: date
    medical_history: MedicalHistory  # Value Object
    smoking_history: SmokingHistory  # Value Object

    def calculate_age(self) -> int:
        """計算當前年齡"""
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def calculate_bmi(self) -> BMI | None:
        """計算 BMI"""
        if not self.height_cm or not self.weight_kg:
            return None
        return BMI(self.weight_kg, self.height_cm)
```

**實際程式碼** (`backend/src/respira_ally/domain/entities/patient.py`):
```python
# 檔案只有 1 行（幾乎是空的）
```

**實際邏輯位置**: `backend/src/respira_ally/application/patient/patient_service.py`
```python
class PatientService:
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        # 業務邏輯在 Application Layer，而非 Domain Layer
        ...

    @staticmethod
    def calculate_bmi(weight_kg: Decimal | None, height_cm: int | None) -> Decimal | None:
        # 業務邏輯在 Application Layer，而非 Domain Layer
        ...
```

**評估**: ❌ **嚴重不符**

**影響分析**:
1. **違反 DDD 原則**: 業務邏輯（年齡計算、BMI 計算）應封裝在 Domain Entity 中，而非 Application Service
2. **違反 Clean Architecture**: Domain Layer 應包含所有業務規則
3. **測試複雜度增加**: 業務邏輯測試必須依賴 Application Service，而非純 Domain Entity

---

### 1.2 Value Objects (值物件)

#### ❌ BMI Value Object - **完全缺失**

**文件描述** (10_class_relationships.md, 行 1598-1655):
```python
@dataclass(frozen=True)
class BMI:
    """BMI Value Object - 封裝 BMI 計算與分類邏輯"""
    value: Decimal

    def __post_init__(self):
        if not (10 <= self.value <= 50):
            raise ValueError(f"BMI must be between 10-50, got {self.value}")

    def category(self) -> str:
        """BMI 分類"""
        if self.value < 18.5:
            return "underweight"
        elif self.value < 24:
            return "normal"
        elif self.value < 27:
            return "overweight"
        else:
            return "obese"
```

**實際程式碼** (`backend/src/respira_ally/domain/value_objects/bmi.py`):
```python
# 檔案只有 1 行（幾乎是空的）
```

**評估**: ❌ **完全缺失**

---

#### ❌ MedicalHistory Value Object - **完全缺失**

**實際程式碼** (`backend/src/respira_ally/domain/value_objects/medical_history.py`):
```python
# 檔案只有 1 行（幾乎是空的）
```

**評估**: ❌ **完全缺失**

---

#### ❌ SmokingHistory Value Object - **完全缺失**

**實際程式碼** (`backend/src/respira_ally/domain/value_objects/smoking_history.py`):
```python
# 檔案只有 1 行（幾乎是空的）
```

**評估**: ❌ **完全缺失**

---

**Value Objects 影響分析**:
1. **缺乏型別安全**: BMI 使用原始型別 `Decimal` 而非封裝的 Value Object
2. **驗證邏輯分散**: BMI 驗證邏輯（範圍檢查、分類）散落各處
3. **可測試性降低**: 無法單獨測試 Value Object 的不變性 (immutability) 和驗證邏輯

---

### 1.3 Repository Interfaces (倉儲介面)

#### ✅ PatientRepository - **基本符合**，但有 DIP 違反

**文件描述** (10_class_relationships.md, 行 1213-1350):
```python
# 文件中的介面名稱是 IPatientRepository
class IPatientRepository(ABC):
    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Patient | None:
        pass
```

**實際程式碼** (`backend/src/respira_ally/domain/repositories/patient_repository.py`):
```python
class PatientRepository(ABC):  # 名稱不同，但可接受
    @abstractmethod
    async def create(self, patient: PatientProfileModel) -> PatientProfileModel:
        # ⚠️ 使用 Infrastructure Layer 的 ORM Model，而非 Domain Entity
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> PatientProfileModel | None:
        # ⚠️ 返回 ORM Model，而非 Domain Entity
        pass
```

**評估**: ⚠️ **基本符合，但違反 DIP**

**DIP 違反分析**:
- **問題**: Domain Layer 的 Repository 介面引用了 Infrastructure Layer 的 `PatientProfileModel`
- **違反原則**: Dependency Inversion Principle - Domain Layer 不應依賴 Infrastructure Layer
- **影響**:
  - Domain Layer 與 Infrastructure Layer 耦合
  - 無法輕易替換資料庫實作（如從 PostgreSQL 換到 MongoDB）
  - 測試時必須引入 ORM 依賴

**正確做法** (根據文件):
```python
# Domain Layer: 使用純 Domain Entity
class PatientRepository(ABC):
    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        # 使用 Domain Entity，而非 ORM Model
        pass
```

```python
# Infrastructure Layer: Adapter 負責轉換
class PatientRepositoryImpl(PatientRepository):
    async def create(self, patient: Patient) -> Patient:
        # 1. 轉換 Domain Entity → ORM Model
        orm_model = self._to_orm(patient)
        # 2. 資料庫操作
        self.db.add(orm_model)
        await self.db.commit()
        # 3. 轉換 ORM Model → Domain Entity
        return self._to_domain(orm_model)
```

---

### 1.4 Domain Services (領域服務)

#### ✅ RiskAssessmentService - **完全符合**（命名略有不同）

**文件描述** (10_class_relationships.md, 行 771-795):
```python
class RiskEngine:  # 文件中的名稱
    def calculate_risk(self, input_data: RiskInput) -> RiskResult:
        # GOLD ABE 分類邏輯
        ...
```

**實際程式碼** (`backend/src/respira_ally/domain/services/risk_assessment_service.py`):
```python
class RiskAssessmentService:  # 實際名稱略有不同
    def calculate_risk(self, input_data: RiskAssessmentInput) -> RiskAssessmentResult:
        """
        GOLD ABE Classification Logic (GOLD 2011):
        - Group A (Low Risk): CAT<10 AND mMRC<2
        - Group B (Medium Risk): CAT>=10 OR mMRC>=2 (but not both)
        - Group E (High Risk): CAT>=10 AND mMRC>=2
        """
        gold_group = self._classify_gold_group(input_data.cat_score, input_data.mmrc_grade)
        risk_score, risk_level = self._map_to_legacy_risk(gold_group)
        # ...
```

**評估**: ✅ **功能完全符合**，命名略有不同

**亮點**:
- ✅ 使用 `@dataclass(frozen=True)` 確保 Input/Output 不可變
- ✅ 純函數設計，無副作用
- ✅ 正確實作 GOLD ABE 分類
- ✅ 包含 Linus Torvalds 引言註解
- ✅ 符合「Good Taste」原則（使用 dict mapping 消除 if-else）

---

## 2. Application Layer (應用層) 分析

### 2.1 Application Services

#### ✅ PatientService - **符合**（但承擔了過多 Domain 邏輯）

**文件描述** (09_module_dependency_analysis.md, 行 68-85):
```python
class PatientService:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo  # 依賴注入抽象
```

**實際程式碼** (`backend/src/respira_ally/application/patient/patient_service.py`):
```python
class PatientService:
    def __init__(
        self,
        patient_repository: PatientRepository,
        event_publisher: EventPublisher | None = None,
    ):
        self.patient_repo = patient_repository  # ✅ DI 正確
        self.event_publisher = event_publisher

    @staticmethod
    def calculate_age(birth_date: date) -> int:
        # ⚠️ 這應該是 Patient Entity 的方法，而非 Service
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @staticmethod
    def calculate_bmi(weight_kg: Decimal | None, height_cm: int | None) -> Decimal | None:
        # ⚠️ 這應該是 BMI Value Object 或 Patient Entity 的方法
        if not weight_kg or not height_cm:
            return None
        height_m = Decimal(height_cm) / Decimal(100)
        bmi = weight_kg / (height_m * height_m)
        return round(bmi, 1)
```

**評估**: ✅ **DI 正確**，但 ⚠️ **承擔了過多 Domain 邏輯**

**問題分析**:
- `calculate_age()` 和 `calculate_bmi()` 是業務邏輯，應屬於 Domain Layer
- Application Service 應該只負責編排（orchestration），不應包含業務規則
- 這違反了 Clean Architecture 的職責分離原則

---

## 3. Infrastructure Layer (基礎設施層) 分析

### 3.1 Repository Implementations

#### ✅ PatientRepositoryImpl - **完全符合**

**實際程式碼** (`backend/src/respira_ally/infrastructure/repository_impls/patient_repository_impl.py`):
```python
class PatientRepositoryImpl(PatientRepository):  # ✅ 繼承抽象介面
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, patient: PatientProfileModel) -> PatientProfileModel:
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    # ... 所有抽象方法都正確實作
```

**評估**: ✅ **完全符合** Repository Pattern

**亮點**:
- ✅ 正確繼承抽象介面
- ✅ 所有方法都正確實作
- ✅ 使用 SQLAlchemy AsyncSession
- ✅ 正確處理分頁、篩選、排序

---

## 4. Frontend (前端) 分析

### 4.1 TypeScript 型別定義

#### ✅ Patient Types - **與後端對齊**

**實際程式碼** (`frontend/dashboard/lib/types/patient.ts`):
```typescript
export interface PatientResponse extends PatientBase {
  user_id: string  // ✅ 與後端 PatientResponse 對應
  therapist_id?: string

  // GOLD ABE Risk Assessment (Sprint 4)
  gold_group?: GoldGroup  // ✅ 正確定義
  latest_risk_assessment?: RiskAssessmentSummary

  // Exacerbation history (Sprint 4)
  exacerbation_count_last_12m?: number  // ✅ 與後端對應
  hospitalization_count_last_12m?: number
  last_exacerbation_date?: string
}

export enum GoldGroup {
  A = 'A',  // ✅ 與後端 GOLD ABE 一致
  B = 'B',
  E = 'E',
}
```

**評估**: ✅ **完全對齊** 後端 Pydantic Schemas

---

### 4.2 API Client

#### ✅ Patients API - **端點正確**

**實際程式碼** (`frontend/dashboard/lib/api/patients.ts`):
```typescript
export const patientsApi = {
  async getPatients(params?: PatientsQuery): Promise<PatientListResponse> {
    return apiClient.get<PatientListResponse>('/patients', { params })
  },

  async getPatient(patientId: string): Promise<PatientResponse> {
    return apiClient.get<PatientResponse>(`/patients/${patientId}`)
    // ✅ 使用 {patient_id}，與修正後的 API 文件一致
  },
}
```

**評估**: ✅ **完全符合** API 設計規範

---

## 5. 文件品質評估

### 5.1 文件 09 (Module Dependency Analysis)

**優點**:
- ✅ 清楚闡述 Clean Architecture 原則
- ✅ 提供具體的 DIP 範例
- ✅ 詳細的依賴關係圖

**問題**:
- ❌ 過度理想化 - 描述了完整的 Domain Entity 和 Value Objects，但實際未實作
- ❌ 未說明實作現狀 - 沒有標註哪些是「已實作」vs「規劃中」
- ⚠️ DIP 範例與實際程式碼不符 - 文件展示純 Domain Entity，實際使用 ORM Model

**建議**:
1. 新增「實作狀態」章節，標註每個模組的實作進度
2. 區分「Phase 0-2 (Current)」vs「Phase 3+ (Future)」的架構
3. 更新 DIP 範例以反映實際程式碼

---

### 5.2 文件 10 (Class Relationships and Module Design)

**優點**:
- ✅ 提供詳細的 UML 類別圖
- ✅ 包含完整的程式碼範例
- ✅ 清楚說明各層職責

**問題**:
- ❌ **程式碼範例與實際程式碼嚴重不符**:
  - Patient Entity 範例 (行 1422-1595) - 實際只有1行
  - BMI Value Object 範例 (行 1598-1655) - 實際只有1行
  - MedicalHistory, SmokingHistory 範例 - 實際都是空檔案
- ❌ 未說明這些是「設計願景」還是「實際實作」
- ⚠️ `RiskEngine` vs `RiskAssessmentService` 命名不一致

**建議**:
1. 在每個程式碼範例前標註 `[已實作]` 或 `[規劃中]`
2. 將「設計願景」移到獨立章節，與「實際實作」區分
3. 更新類別名稱以反映實際程式碼

---

## 6. 架構違反分析

### 6.1 違反 Dependency Inversion Principle

**違反點**: `PatientRepository` (Domain Layer) 引用 `PatientProfileModel` (Infrastructure Layer)

**檔案**: `backend/src/respira_ally/domain/repositories/patient_repository.py`

```python
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
# ⚠️ Domain Layer 引用 Infrastructure Layer - 違反 DIP

class PatientRepository(ABC):
    @abstractmethod
    async def create(self, patient: PatientProfileModel) -> PatientProfileModel:
        # ⚠️ 應該使用 Domain Entity，而非 ORM Model
        pass
```

**影響**:
1. **耦合度高**: Domain Layer 與 SQLAlchemy ORM 耦合
2. **難以測試**: 測試 Domain Logic 必須引入 ORM
3. **難以替換**: 無法輕易切換資料庫技術

**修正建議**:
```python
# Domain Layer: 純 Domain Entity
from respira_ally.domain.entities.patient import Patient

class PatientRepository(ABC):
    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        pass
```

```python
# Infrastructure Layer: Adapter 負責轉換
class PatientRepositoryImpl(PatientRepository):
    def _to_orm(self, entity: Patient) -> PatientProfileModel:
        # Domain Entity → ORM Model
        ...

    def _to_domain(self, model: PatientProfileModel) -> Patient:
        # ORM Model → Domain Entity
        ...

    async def create(self, patient: Patient) -> Patient:
        orm_model = self._to_orm(patient)
        self.db.add(orm_model)
        await self.db.commit()
        return self._to_domain(orm_model)
```

---

### 6.2 違反 Domain-Driven Design 原則

**違反點**: 業務邏輯散落在 Application Service

**問題**:
- `PatientService.calculate_age()` - 應在 `Patient` Entity
- `PatientService.calculate_bmi()` - 應在 `BMI` Value Object 或 `Patient` Entity

**影響**:
1. **Domain Layer 貧血** (Anemic Domain Model)
2. **業務邏輯分散**，難以維護
3. **測試複雜度增加**

**修正建議**:
```python
# Domain Entity
@dataclass
class Patient:
    birth_date: date
    height_cm: int | None
    weight_kg: Decimal | None

    def calculate_age(self) -> int:
        """業務邏輯：年齡計算"""
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def calculate_bmi(self) -> BMI | None:
        """業務邏輯：BMI 計算"""
        if not self.height_cm or not self.weight_kg:
            return None
        return BMI(self.weight_kg, self.height_cm)
```

```python
# Application Service - 只負責編排
class PatientService:
    async def get_patient_by_id(self, user_id: UUID) -> PatientResponse:
        patient = await self.patient_repo.get_by_id(user_id)

        # 業務邏輯由 Domain Entity 負責
        age = patient.calculate_age()
        bmi = patient.calculate_bmi()

        return PatientResponse(
            age=age,
            bmi=bmi.value if bmi else None,
            ...
        )
```

---

## 7. 優先級修正建議

### 🔴 高優先級 (Phase 0 - 核心驗證)

**1. 實作 Patient Domain Entity**
- **檔案**: `backend/src/respira_ally/domain/entities/patient.py`
- **內容**: 實作 `Patient` dataclass，包含 `calculate_age()`, `calculate_bmi()` 方法
- **影響**: 修正 DDD 違反，業務邏輯回歸 Domain Layer

**2. 修正 Repository 的 DIP 違反**
- **檔案**: `backend/src/respira_ally/domain/repositories/patient_repository.py`
- **內容**: Repository 介面使用 `Patient` Entity 而非 `PatientProfileModel`
- **影響**: 解除 Domain Layer 對 Infrastructure Layer 的依賴

**3. 更新文件狀態標註**
- **檔案**: `docs/09_module_dependency_analysis.md`, `docs/10_class_relationships_and_module_design.md`
- **內容**: 在每個模組/類別前標註 `[已實作]` 或 `[規劃中]`
- **影響**: 讀者能清楚了解實作現狀

---

### 🟡 中優先級 (Phase 1-2)

**4. 實作核心 Value Objects**
- **檔案**:
  - `backend/src/respira_ally/domain/value_objects/bmi.py`
  - `backend/src/respira_ally/domain/value_objects/medical_history.py`
  - `backend/src/respira_ally/domain/value_objects/smoking_history.py`
- **內容**: 實作 Value Objects，封裝驗證邏輯
- **影響**: 提升型別安全，集中驗證邏輯

**5. 重構 PatientService**
- **檔案**: `backend/src/respira_ally/application/patient/patient_service.py`
- **內容**: 移除 `calculate_age()`, `calculate_bmi()` 靜態方法，改用 Patient Entity
- **影響**: Application Service 專注於編排，不包含業務邏輯

---

### 🟢 低優先級 (Phase 3+)

**6. 統一類別命名**
- **檔案**: `backend/src/respira_ally/domain/services/risk_assessment_service.py`
- **內容**: `RiskAssessmentService` → `RiskEngine` (或更新文件)
- **影響**: 文件與程式碼命名一致

**7. 補充前端架構文件**
- **檔案**: `docs/10_class_relationships_and_module_design.md`
- **內容**: 新增 Frontend 組件架構、狀態管理、API 整合章節
- **影響**: 前端架構有文件支援

---

## 8. 結論與建議

### 8.1 整體架構健康度

**分數**: 6.5 / 10

**優點**:
- ✅ Repository Pattern 正確實作
- ✅ Application Services 正確使用 DI
- ✅ Risk Assessment 使用 GOLD ABE 標準分類
- ✅ 前端型別定義與後端對齊
- ✅ DailyLog Entity 是 DDD 的典範實作

**缺點**:
- ❌ Patient Entity 未實作 (僅空檔案)
- ❌ 所有 Value Objects 未實作
- ❌ 違反 Dependency Inversion Principle
- ❌ 業務邏輯散落在 Application Service (Anemic Domain Model)
- ❌ 文件描述與實際程式碼嚴重不符

---

### 8.2 文件定位建議

**當前問題**: 文件 09 和 10 介於「設計文件」與「實作文件」之間，導致混淆

**建議分離**:

1. **設計願景文件** (`docs/architecture/design_vision.md`):
   - 描述理想的 Clean Architecture 實作
   - 包含完整的 Domain Entities, Value Objects 範例
   - 標註為「Phase 3+ 目標」

2. **實作現狀文件** (`docs/architecture/implementation_status.md`):
   - 描述 Phase 0-2 (MVP) 的實際實作
   - 明確標註每個模組的實作狀態
   - 包含實際程式碼範例（非願景範例）

3. **架構演進計畫** (`docs/architecture/evolution_plan.md`):
   - 從 Modular Monolith → Microservices 的演進路徑
   - 從 Anemic Domain Model → Rich Domain Model 的重構計畫
   - 每個 Phase 的架構里程碑

---

### 8.3 Linus Torvalds 視角的架構評估

基於 CLAUDE.md 中的 Linus 哲學：

#### 🟢 Good Taste (好品味)

**優點**:
- `RiskAssessmentService` 使用 dict mapping 消除 if-else - ✅ 符合「消除特殊情況」
- `DailyLog` 使用 `__post_init__` 集中驗證邏輯 - ✅ 符合「簡潔執念」

**問題**:
- Patient Entity 空白，業務邏輯散落 - ❌ 違反「Good Taste」
- 資料結構不完整 (缺少 Value Objects) - ❌ "Bad programmers worry about the code. Good programmers worry about data structures."

#### 🟡 Never Break Userspace (向後相容)

**優點**:
- GOLD ABE 引入時保留 legacy `risk_score`/`risk_level` - ✅ 符合「Never break userspace」
- 前端 API 端點未變更 (`/patients/{patient_id}`) - ✅ 符合向後相容

**問題**:
- DIP 違反導致難以替換資料庫 - ⚠️ 未來重構會破壞相容性

#### 🟡 Practicality Beats Purity (實用主義)

**優點**:
- Modular Monolith 而非微服務 - ✅ 符合「解決實際問題」
- 使用 ORM Model 而非純 Domain Entity - ✅ 務實選擇（暫時）

**問題**:
- 空的 Value Objects 檔案應刪除或實作 - ❌ "不存在的威脅"（空檔案無用）

#### ❌ Simplicity is Prerequisite (簡潔執念)

**問題**:
- PatientService 承擔過多職責 (業務邏輯 + 編排) - ❌ 違反「函式只做一件事」
- Repository 介面與實作耦合 ORM - ❌ 增加複雜度

---

### 8.4 最終建議

**立即行動** (本週內):
1. 在文件 09 和 10 的開頭新增「實作狀態總覽」表格
2. 實作 `Patient` Entity 基本結構（不需完整，但不能空白）
3. 移除或補全空的 Value Objects 檔案（避免誤導）

**短期目標** (Sprint 6):
4. 修正 DIP 違反 - Repository 使用 Domain Entity
5. 重構 PatientService - 業務邏輯移至 Patient Entity

**長期願景** (Phase 3+):
6. 實作完整的 Value Objects
7. 建立 Domain Event 系統
8. 準備 Microservices 拆分

---

## 附錄：檔案清單

### 已檢查的檔案

**後端 Domain Layer**:
- ✅ `backend/src/respira_ally/domain/entities/daily_log.py` (完整)
- ❌ `backend/src/respira_ally/domain/entities/patient.py` (空白)
- ❌ `backend/src/respira_ally/domain/entities/risk_score.py` (空白)
- ❌ `backend/src/respira_ally/domain/value_objects/bmi.py` (空白)
- ❌ `backend/src/respira_ally/domain/value_objects/medical_history.py` (空白)
- ❌ `backend/src/respira_ally/domain/value_objects/smoking_history.py` (空白)
- ⚠️ `backend/src/respira_ally/domain/repositories/patient_repository.py` (DIP違反)
- ✅ `backend/src/respira_ally/domain/services/risk_assessment_service.py` (完整)

**後端 Application Layer**:
- ✅ `backend/src/respira_ally/application/patient/patient_service.py` (完整)

**後端 Infrastructure Layer**:
- ✅ `backend/src/respira_ally/infrastructure/repository_impls/patient_repository_impl.py` (完整)
- ✅ `backend/src/respira_ally/infrastructure/database/models/patient_profile.py` (完整)

**前端**:
- ✅ `frontend/dashboard/lib/types/patient.ts` (完整)
- ✅ `frontend/dashboard/lib/types/kpi.ts` (完整)
- ✅ `frontend/dashboard/lib/api/patients.ts` (完整)
- ✅ `frontend/dashboard/lib/api/kpi.ts` (完整)

**文件**:
- 📄 `docs/09_module_dependency_analysis.md` (711 行)
- 📄 `docs/10_class_relationships_and_module_design.md` (1808 行)

---

**報告結束**

**下一步**: 請決定優先修正項目並建立行動計畫。
