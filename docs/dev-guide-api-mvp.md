# API MVP 開發指南 (API MVP Development Guide)

**文件版本 (Version)**: v1.0
**最後更新 (Last Updated)**: 2025-10-20
**適用階段 (Applied Phase)**: Sprint 2-4 (快速迭代期)
**核心理念 (Core Philosophy)**: Linus Torvalds - "Practicality Beats Purity"

---

## 🎯 目的與範圍

本指南定義 **2人團隊、快速迭代環境** 下的 API 開發最佳實踐。

**核心目標**：
1. **高效交付**：快速實現可運行的 API 端點
2. **保持條理**：不因求快而讓代碼混亂
3. **漸進式重構**：等重複 3 次再抽象，不過早優化

---

## 📐 開發原則 (Development Principles)

### 原則 1: Router 優先，Use Case 按需

❌ **避免**：一開始就寫完整的 4 層架構
```python
# ❌ 過早抽象
class CreatePatientUseCase:
    def __init__(self, repo: PatientRepository, validator: PatientValidator, ...):
        # 10 個依賴注入

    async def execute(self, data: PatientCreate) -> Patient:
        # 100 行邏輯
```

✅ **推薦**：先在 Router 實作，等重複 3 次再抽取
```python
# ✅ 先讓它工作
@router.post("/patients", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_therapist)
):
    # 驗證邏輯 (10-20 行)
    therapist = await db.get(TherapistProfile, data.therapist_id)
    if not therapist:
        raise HTTPException(404, "Therapist not found")

    # 創建實體
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient
```

**何時重構到 Use Case？**
- 同一邏輯在 3 個以上端點重複時
- 端點函數超過 50 行時
- 需要跨服務調用時

---

### 原則 2: 測試覆蓋率：先 Happy Path，再 Edge Case

**測試優先級**：
1. **P0**: Happy Path（80%重要性） - 最常見的使用情境
2. **P1**: 關鍵錯誤情況（15%重要性） - 404, 403, 409 等
3. **P2**: 邊界值與極端情況（5%重要性） - 留給專職 QA

**範例**：
```python
# P0: Happy Path (必須寫)
@pytest.mark.asyncio
async def test_create_patient_success(client, therapist_token):
    response = await client.post("/api/v1/patients", json={...})
    assert response.status_code == 201

# P1: 關鍵錯誤 (必須寫)
@pytest.mark.asyncio
async def test_create_patient_invalid_therapist(client, therapist_token):
    response = await client.post("/api/v1/patients", json={
        "therapist_id": str(uuid4())  # 不存在
    })
    assert response.status_code == 404

# P2: 邊界值 (選擇性)
@pytest.mark.asyncio
async def test_create_patient_name_too_long(client, therapist_token):
    response = await client.post("/api/v1/patients", json={
        "full_name": "a" * 101  # 超過 100 字元
    })
    assert response.status_code == 422
```

**目標覆蓋率**：
- Sprint 2-3: 50% (關注核心流程)
- Sprint 4-5: 65% (增加錯誤處理)
- Sprint 6+: 80% (完整測試)

---

### 原則 3: Schema 驗證 > 手寫驗證

使用 Pydantic 的內建驗證，避免手寫 if-else。

❌ **避免**：
```python
@router.post("/daily-logs")
async def create_log(data: dict, db: AsyncSession):
    if data["water_intake_ml"] < 0:
        raise HTTPException(422, "Water intake must be positive")
    if data["water_intake_ml"] > 4000:
        raise HTTPException(422, "Water intake cannot exceed 4000ml")
    if data["cough_level"] not in range(0, 11):
        raise HTTPException(422, "Cough level must be 0-10")
    # ...
```

✅ **推薦**：
```python
class DailyLogCreate(BaseModel):
    water_intake_ml: int = Field(..., ge=0, le=4000, description="飲水量 0-4000ml")
    cough_level: int = Field(..., ge=0, le=10, description="咳嗽程度 0-10")
    medication_taken: bool

@router.post("/daily-logs")
async def create_log(data: DailyLogCreate, db: AsyncSession):
    # Pydantic 已經驗證，直接使用
    log = DailyLog(**data.model_dump())
    # ...
```

---

### 原則 4: 權限檢查模式化

**標準模式**：
```python
# 模式 1: 只有治療師可執行
async def list_patients(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_therapist)  # 依賴注入檢查
):
    # current_user 保證是 therapist

# 模式 2: 治療師或本人可執行
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    # 權限檢查
    if current_user.role == UserRole.THERAPIST:
        if patient.therapist_id != current_user.user_id:
            raise HTTPException(403, "Access denied")
    elif current_user.role == UserRole.PATIENT:
        if patient.patient_id != current_user.user_id:
            raise HTTPException(403, "Access denied")

    return patient
```

**Dependency 定義**：
```python
# backend/src/respira_ally/api/dependencies/auth.py

async def get_current_therapist(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """只允許治療師通過"""
    if current_user.role != UserRole.THERAPIST:
        raise HTTPException(403, "Therapist access required")
    return current_user
```

---

### 原則 5: 錯誤處理標準化

**HTTP 狀態碼對應表**：

| 狀態碼 | 情境 | 範例 |
|--------|------|------|
| 200 | 成功查詢 | GET /patients |
| 201 | 成功創建 | POST /patients |
| 204 | 成功刪除 | DELETE /patients/{id} |
| 400 | 客戶端請求錯誤 | 缺少必填欄位 |
| 401 | 未認證 | Token 無效或過期 |
| 403 | 已認證但無權限 | 治療師 A 查看治療師 B 的病患 |
| 404 | 資源不存在 | GET /patients/{invalid-id} |
| 409 | 資源衝突 | 重複創建相同日期的日誌 |
| 422 | 驗證失敗 | 飲水量 4001ml |
| 500 | 伺服器內部錯誤 | 資料庫連線失敗 |

**標準錯誤格式**：
```python
from fastapi import HTTPException

# 標準用法
raise HTTPException(status_code=404, detail="Patient not found")

# 帶額外資訊
raise HTTPException(
    status_code=409,
    detail={
        "error": "duplicate_log",
        "message": "Log already exists for this date",
        "date": "2025-10-20"
    }
)
```

---

## 🚀 開發流程 (Development Workflow)

### Step 1: Schema 定義（15min）
```python
# 1. Base Schema (共用欄位)
class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    gender: Literal["M", "F", "OTHER"]
    date_of_birth: date

# 2. Create Schema (創建時需要的欄位)
class PatientCreate(PatientBase):
    therapist_id: UUID

# 3. Response Schema (API 回應格式)
class PatientResponse(PatientBase):
    patient_id: UUID
    therapist_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # 支援 ORM 轉換
```

### Step 2: Database Model（15min）
```python
# backend/src/respira_ally/infrastructure/database/models/patient.py

class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    therapist_id: Mapped[UUID] = mapped_column(
        ForeignKey("therapist_profiles.therapist_id"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # 關聯
    therapist = relationship("TherapistProfile", back_populates="patients")
```

### Step 3: API 端點（30-60min）
```python
# backend/src/respira_ally/api/v1/routers/patient.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from respira_ally.core.schemas.patient import PatientCreate, PatientResponse
from respira_ally.infrastructure.database.models.patient import Patient
from respira_ally.api.dependencies.database import get_db
from respira_ally.api.dependencies.auth import get_current_therapist, get_current_user

router = APIRouter()

@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_therapist)
):
    """創建新病患（只有治療師可執行）"""
    # 1. 驗證治療師存在
    therapist = await db.get(TherapistProfile, data.therapist_id)
    if not therapist:
        raise HTTPException(404, "Therapist not found")

    # 2. 創建病患
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """查詢單一病患"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    # 權限檢查
    if current_user.role == UserRole.THERAPIST:
        if patient.therapist_id != current_user.user_id:
            raise HTTPException(403, "Access denied")
    elif current_user.role == UserRole.PATIENT:
        if patient.patient_id != current_user.user_id:
            raise HTTPException(403, "Access denied")

    return patient

@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0, description="分頁偏移量"),
    limit: int = Query(20, ge=1, le=100, description="每頁數量"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_therapist)
):
    """列出病患（分頁，只有治療師可執行）"""
    stmt = (
        select(Patient)
        .where(Patient.therapist_id == current_user.user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Patient.created_at.desc())
    )
    result = await db.execute(stmt)
    patients = result.scalars().all()
    return patients
```

### Step 4: 單元測試（30min）
```python
# backend/tests/api/v1/test_patient.py

@pytest.mark.asyncio
async def test_create_patient_success(client, therapist_token, therapist_user_id):
    """測試創建病患成功"""
    response = await client.post(
        "/api/v1/patients",
        json={
            "full_name": "John Doe",
            "gender": "M",
            "date_of_birth": "1960-05-15",
            "therapist_id": str(therapist_user_id)
        },
        headers={"Authorization": f"Bearer {therapist_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert "patient_id" in data

@pytest.mark.asyncio
async def test_get_patient_unauthorized(client, patient_token, other_patient_id):
    """測試查詢病患 - 權限不足"""
    response = await client.get(
        f"/api/v1/patients/{other_patient_id}",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 403
```

---

## ✅ 檢查清單 (Checklist)

每完成一個 API 端點，確認：

**功能完整性**：
- [ ] Schema 定義完整（Create, Response）
- [ ] Database Model 對應 Schema
- [ ] API 端點實作（包含錯誤處理）
- [ ] 權限檢查正確實作

**測試覆蓋**：
- [ ] 至少 1 個 Happy Path 測試
- [ ] 至少 1 個錯誤情況測試（404/403/409）
- [ ] 邊界值測試（數值範圍、字串長度）

**代碼品質**：
- [ ] 函數長度 < 50 行
- [ ] 無重複代碼（DRY 原則）
- [ ] Type hints 完整
- [ ] Docstring 說明清楚

**手動驗證**：
- [ ] 使用 curl 或 Postman 測試成功
- [ ] 檢查回應格式符合 Schema
- [ ] 確認錯誤訊息清晰易懂

---

## 🔧 常見問題 (FAQ)

### Q1: 何時需要寫 Repository？
**A**: 當同一個資料查詢邏輯在 3 個以上端點重複時。

### Q2: 何時需要寫 Domain Service？
**A**: 當業務規則跨越多個聚合（Aggregate）時，例如：
- 風險分數計算（需要日誌、問卷、病患資料）
- 服藥遵從率計算（需要多天日誌）

### Q3: 如何處理複雜查詢？
**A**: 先在 Router 直接寫 SQLAlchemy 查詢，等重複 3 次再抽到 Repository。

### Q4: 是否需要 DTO 層？
**A**: Pydantic Schema 已經是 DTO，不需要額外的 DTO 類別。

### Q5: 如何處理 N+1 查詢問題？
**A**: 使用 SQLAlchemy 的 `selectinload` 或 `joinedload`：
```python
from sqlalchemy.orm import selectinload

stmt = (
    select(Patient)
    .options(selectinload(Patient.therapist))  # 預載入關聯
    .where(Patient.therapist_id == therapist_id)
)
```

---

## 📚 參考資源

- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文檔](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2 文檔](https://docs.pydantic.dev/latest/)
- [Clean Architecture 原則](../05_architecture_and_design.md)
- [API 設計規範](../06_api_design_specification.md)

---

**最後更新**: 2025-10-20 by TaskMaster Hub
**版本歷史**:
- v1.0 (2025-10-20): 初始版本，定義 Sprint 2-4 開發規範
