# 代碼審查與重構指南 (Code Review & Refactoring Guide) - RespiraAlly V2.0

---

**文件版本:** v1.0
**最後更新:** 2025-10-19
**主要作者:** Claude Code AI - Tech Lead
**狀態:** Sprint 0 → Sprint 1 轉換期

---

## 🎯 目的 (Purpose)

本文檔建立 RespiraAlly V2.0 的代碼審查標準與重構準則，確保：

- ✅ **代碼品質**: 可讀、可維護、可測試
- ✅ **架構一致性**: 遵循 Clean Architecture + DDD
- ✅ **依賴健康**: 無循環依賴、依賴倒置原則
- ✅ **技術債管理**: 每 Sprint 保留 20% 時間重構

---

## 🔍 Code Review 流程 (Review Process)

### 階段 1: 開發者自審 (Self-Review)

**提交 PR 前必須完成**:

```bash
# 1. 代碼格式化
uv run black backend/
uv run ruff check backend/ --fix

# 2. 類型檢查
uv run mypy backend/

# 3. 測試執行
uv run pytest --cov=backend --cov-report=term-missing

# 4. 依賴檢查
pydeps backend/app --max-bacon=2 --no-output

# 5. 安全掃描 (可選)
uv run bandit -r backend/
```

**自審檢查清單**:

- [ ] 所有測試通過 (覆蓋率 ≥ 80%)
- [ ] 代碼格式符合 Black/Ruff 標準
- [ ] Mypy 無類型錯誤
- [ ] 無循環依賴 (pydeps 檢查)
- [ ] 已撰寫或更新相關文檔
- [ ] Commit Message 符合 Conventional Commits
- [ ] PR Description 清楚說明變更原因

### 階段 2: Peer Review (同儕審查)

**SLA (Service Level Agreement)**:
- **回應時間**: < 4 小時 (工作時間內)
- **完成時間**: < 24 小時
- **阻塞性問題**: < 1 小時回應

**審查分工**:
- **Backend PR**: Backend Lead 必審，+1 其他成員
- **Frontend PR**: Frontend Lead 必審，+1 其他成員
- **架構變更**: System Architect 必審
- **安全相關**: Security Engineer 必審

---

## 📋 Review 檢查清單 (Review Checklist)

### 1. 代碼品質 (Code Quality)

#### 1.1 可讀性 (Readability)

**審查問題**:
- ❓ 變數名稱是否清楚表達意圖？
- ❓ 函數名稱是否遵循「動詞 + 名詞」命名？
- ❓ 複雜邏輯是否有註解說明？
- ❓ 是否有 Magic Number (應使用常數)？

**範例**:

```python
# ❌ 不好的命名
def calc(p, d):
    r = p.s + p.a - d  # What is r? s? a?
    return r

# ✅ 好的命名
def calculate_risk_score(patient: Patient, daily_log: DailyLog) -> RiskScore:
    """計算病患風險分數

    Args:
        patient: 病患實體
        daily_log: 當日日誌

    Returns:
        RiskScore: 風險分數 (0-100)
    """
    symptom_score = patient.symptom_severity
    activity_score = patient.activity_level
    decline_factor = daily_log.health_decline

    total_risk = symptom_score + activity_score - decline_factor
    return RiskScore(value=total_risk)
```

#### 1.2 複雜度 (Complexity)

**檢查標準**:
- ⚠️ 函數行數 > 30 → 需拆分
- ⚠️ 嵌套層數 > 3 → 需重構
- ⚠️ 圈複雜度 > 10 → 需簡化
- ⚠️ 函數參數 > 4 → 考慮使用物件封裝

**工具檢測**:

```bash
# 使用 radon 檢查複雜度
pip install radon
radon cc backend/ -s -a
```

**範例 - 降低嵌套層數**:

```python
# ❌ 3 層嵌套
def process_patient(patient_id: int):
    patient = get_patient(patient_id)
    if patient:
        if patient.is_active:
            if patient.has_daily_log_today():
                calculate_risk(patient)
            else:
                send_reminder(patient)
        else:
            archive_patient(patient)

# ✅ Early Return 降低嵌套
def process_patient(patient_id: int):
    patient = get_patient(patient_id)
    if not patient:
        return

    if not patient.is_active:
        archive_patient(patient)
        return

    if patient.has_daily_log_today():
        calculate_risk(patient)
    else:
        send_reminder(patient)
```

#### 1.3 DRY 原則 (Don't Repeat Yourself)

**審查問題**:
- ❓ 是否有重複的代碼邏輯？
- ❓ 相似的代碼是否可提取為函數？
- ❓ 是否有重複的常數定義？

**範例 - Extract Method**:

```python
# ❌ 重複邏輯
def create_patient_report(patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # ... 業務邏輯

def get_patient_logs(patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # ... 業務邏輯

# ✅ 提取共用函數
def get_patient_or_404(patient_id: int, db: Session) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

def create_patient_report(patient_id: int, db: Session):
    patient = get_patient_or_404(patient_id, db)
    # ... 業務邏輯

def get_patient_logs(patient_id: int, db: Session):
    patient = get_patient_or_404(patient_id, db)
    # ... 業務邏輯
```

---

### 2. 架構與設計 (Architecture & Design)

#### 2.1 Clean Architecture 分層檢查

**檢查清單**:

- [ ] **Presentation Layer**: 是否僅處理 HTTP 請求/響應？
  - ❌ 不應包含業務邏輯
  - ❌ 不應直接訪問數據庫
- [ ] **Application Layer**: 是否僅編排用例？
  - ❌ 不應包含數據庫查詢細節
  - ❌ 不應直接調用外部 API
- [ ] **Domain Layer**: 是否零外部依賴？
  - ✅ 僅包含純業務邏輯
  - ✅ 僅依賴標準庫
- [ ] **Infrastructure Layer**: 是否實現 Domain 定義的介面？
  - ✅ Repository 實現
  - ✅ 外部服務 Adapter

**範例 - 違反分層的代碼**:

```python
# ❌ Presentation Layer 包含業務邏輯 (錯誤)
@router.post("/daily-logs")
async def create_daily_log(request: DailyLogRequest, db: Session):
    # 業務邏輯不應在這裡!
    risk_score = request.symptom_score * 0.6 + request.activity_score * 0.4

    log = DailyLog(
        patient_id=request.patient_id,
        data=request.data,
        risk_score=risk_score  # 風險計算應在 Domain/Application
    )
    db.add(log)
    db.commit()
    return log

# ✅ 正確分層
@router.post("/daily-logs")
async def create_daily_log(
    request: DailyLogRequest,
    service: DailyLogService = Depends(get_daily_log_service)
):
    # Presentation 僅負責調用 Application Service
    log = await service.submit_daily_log(request)
    return log

# Application Layer (services/daily_log_service.py)
class DailyLogService:
    async def submit_daily_log(self, request: DailyLogRequest) -> DailyLog:
        # Domain 計算風險分數
        risk_score = calculate_risk_score(request)  # Domain 業務邏輯

        # Infrastructure 持久化
        log = await self.daily_log_repo.save(DailyLog(
            patient_id=request.patient_id,
            data=request.data,
            risk_score=risk_score
        ))

        # 發布領域事件
        await self.event_bus.publish(DailyLogSubmitted(log.id))
        return log
```

#### 2.2 依賴倒置檢查

**審查問題**:
- ❓ Application Layer 是否依賴具體 Repository 實現？
  - ✅ 應依賴 `PatientRepository` (抽象介面)
  - ❌ 不應依賴 `PostgresPatientRepository` (具體實現)
- ❓ 是否使用依賴注入 (Dependency Injection)？
- ❓ Infrastructure 是否實現 Domain 定義的介面？

**檢查範例**:

```python
# ❌ 違反 DIP - Application 依賴具體實現
from infrastructure.repositories.postgres_patient_repo import PostgresPatientRepository

class PatientService:
    def __init__(self):
        self.repo = PostgresPatientRepository()  # 錯誤!

# ✅ 遵循 DIP - Application 依賴抽象
from domain.repositories.patient_repository import PatientRepository  # 抽象

class PatientService:
    def __init__(self, patient_repo: PatientRepository):  # 依賴抽象介面
        self.patient_repo = patient_repo
```

#### 2.3 事件驅動檢查

**檢查清單**:

- [ ] 跨模組調用是否使用事件？
  - ✅ DailyLog → Risk: 通過 `DailyLogSubmitted` 事件
  - ❌ 不應直接導入 `from risk.calculator import ...`
- [ ] 事件命名是否符合「過去式」？
  - ✅ `DailyLogSubmitted`, `RiskScoreCalculated`
  - ❌ `SubmitDailyLog` (這是命令，不是事件)
- [ ] 事件處理器是否冪等 (Idempotent)？
  - 相同事件重複處理不應造成副作用

**範例 - 模組解耦**:

```python
# ❌ 直接依賴其他模組 (錯誤)
# daily_log/service.py
from risk.calculator import RiskCalculator  # 模組耦合!

class DailyLogService:
    async def submit_log(self, data):
        log = await self.repo.save(data)
        RiskCalculator().calculate(log.patient_id)  # 直接調用

# ✅ 事件驅動解耦 (正確)
# daily_log/service.py
from infrastructure.event_bus import event_bus

class DailyLogService:
    async def submit_log(self, data):
        log = await self.repo.save(data)
        await event_bus.publish(DailyLogSubmitted(
            patient_id=log.patient_id,
            log_id=log.id
        ))  # 發布事件，不知道誰訂閱

# risk/event_handlers.py
@event_bus.subscribe(DailyLogSubmitted)
async def handle_daily_log_submitted(event: DailyLogSubmitted):
    await risk_service.calculate_risk(event.patient_id)
```

---

### 3. 安全性 (Security)

#### 3.1 認證與授權

**檢查清單**:

- [ ] 敏感端點是否需要 JWT 驗證？
  - `@requires_auth` 裝飾器
- [ ] 是否檢查用戶權限？
  - 治療師可訪問所有病患
  - 病患僅可訪問自己的數據
- [ ] 密碼是否正確雜湊？
  - ✅ 使用 `passlib` + `bcrypt`
  - ❌ 不應明文存儲
- [ ] JWT Secret 是否從環境變數讀取？
  - ❌ 不應硬編碼在代碼中

**範例 - 權限檢查**:

```python
# ❌ 無權限檢查 (安全漏洞)
@router.get("/patients/{patient_id}/logs")
async def get_patient_logs(patient_id: int, db: Session):
    logs = db.query(DailyLog).filter(DailyLog.patient_id == patient_id).all()
    return logs  # 任何人都可訪問!

# ✅ 正確的權限檢查
@router.get("/patients/{patient_id}/logs")
async def get_patient_logs(
    patient_id: int,
    db: Session,
    current_user: User = Depends(get_current_user)
):
    # 病患僅可訪問自己的日誌
    if current_user.role == "patient" and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 治療師可訪問所有病患日誌
    logs = db.query(DailyLog).filter(DailyLog.patient_id == patient_id).all()
    return logs
```

#### 3.2 SQL 注入防護

**檢查清單**:

- [ ] 是否使用 ORM (SQLAlchemy) 而非原始 SQL？
- [ ] 若使用原始 SQL，是否使用參數化查詢？
- [ ] 是否有用戶輸入直接拼接到 SQL？

**範例**:

```python
# ❌ SQL 注入漏洞
def get_patient_by_name(name: str, db: Session):
    query = f"SELECT * FROM patients WHERE name = '{name}'"  # 危險!
    result = db.execute(query)

# ✅ 使用 ORM 防護
def get_patient_by_name(name: str, db: Session):
    return db.query(Patient).filter(Patient.name == name).first()

# ✅ 參數化查詢 (若必須用原始 SQL)
def get_patient_by_name(name: str, db: Session):
    query = text("SELECT * FROM patients WHERE name = :name")
    result = db.execute(query, {"name": name})
```

#### 3.3 敏感數據保護

**檢查清單**:

- [ ] 是否有敏感資料在日誌中輸出？
  - ❌ 不應記錄密碼、JWT Token、身份證字號
- [ ] API 響應是否包含不必要的敏感欄位？
  - ❌ 不應返回 `password_hash`
- [ ] 檔案上傳是否檢查檔案類型與大小？

**範例 - 過濾敏感欄位**:

```python
# ❌ 返回所有欄位 (包含敏感資料)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str  # 洩漏雜湊!
    role: str

# ✅ 僅返回必要欄位
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True  # SQLAlchemy Model 轉換
```

---

### 4. 測試 (Testing)

#### 4.1 測試覆蓋率

**檢查標準**:
- ✅ 總覆蓋率 ≥ 80%
- ✅ 關鍵業務邏輯 ≥ 90%
- ✅ Repository 層 ≥ 70% (重點測試複雜查詢)

**檢查命令**:

```bash
uv run pytest --cov=backend --cov-report=html
# 查看 htmlcov/index.html
```

**必須測試的場景**:
- ✅ 正常流程 (Happy Path)
- ✅ 邊界條件 (Boundary Cases)
- ✅ 錯誤處理 (Error Handling)
- ✅ 權限檢查 (Authorization)

#### 4.2 測試品質

**審查問題**:
- ❓ 測試是否獨立？(不依賴其他測試的執行順序)
- ❓ 測試是否可重複？(多次執行結果一致)
- ❓ 測試命名是否清楚？(`test_<功能>_<場景>_<預期結果>`)
- ❓ 是否使用 Mock 隔離外部依賴？

**範例 - 好的測試**:

```python
# ✅ 清楚的測試命名與結構
def test_submit_daily_log_should_trigger_risk_calculation_when_valid_data():
    # Arrange (準備)
    patient = create_test_patient()
    log_data = DailyLogRequest(
        patient_id=patient.id,
        symptom_score=7,
        activity_score=3
    )
    mock_event_bus = Mock()

    # Act (執行)
    service = DailyLogService(event_bus=mock_event_bus)
    result = service.submit_daily_log(log_data)

    # Assert (驗證)
    assert result.patient_id == patient.id
    mock_event_bus.publish.assert_called_once_with(
        DailyLogSubmitted(patient_id=patient.id, log_id=result.id)
    )
```

---

## 🔄 重構指南 (Refactoring Guidelines)

### 何時重構 (When to Refactor)

**觸發條件**:

1. **Code Smells 出現**:
   - 重複代碼 (Duplicated Code)
   - 過長函數 (Long Method)
   - 過大類別 (Large Class)
   - 過長參數列表 (Long Parameter List)
   - 發散式變化 (Divergent Change)

2. **技術債累積**:
   - GitHub Issues 標記為 `tech-debt` 累積 > 5 個
   - Sonar 報告技術債 > 1 天工時

3. **新功能開發困難**:
   - 新增功能需修改 > 3 個不相關檔案
   - 測試覆蓋率下降

**重構時機**:
- ✅ **每 Sprint 保留 20% 時間重構** (約 16-20h)
- ✅ 修 Bug 時順便重構相關代碼
- ❌ 不在 Sprint 最後一天大規模重構

### 重構策略 (Refactoring Techniques)

#### 策略 1: Extract Method (提取函數)

**適用場景**: 函數過長 (> 30 行) 或有重複邏輯

```python
# Before
def calculate_patient_risk(patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    # 計算症狀分數 (10 行)
    symptom_score = 0
    if patient.cough_frequency == "often":
        symptom_score += 20
    if patient.shortness_of_breath == "severe":
        symptom_score += 30
    # ...

    # 計算活動分數 (10 行)
    activity_score = 0
    if patient.walk_distance < 100:
        activity_score += 25
    # ...

    # 計算問卷分數 (10 行)
    survey_score = 0
    latest_survey = db.query(Survey).filter(...).first()
    if latest_survey:
        survey_score = latest_survey.cat_score
    # ...

    total_risk = symptom_score + activity_score + survey_score
    return total_risk

# After
def calculate_patient_risk(patient_id: int):
    patient = get_patient_or_404(patient_id)

    symptom_score = calculate_symptom_score(patient)
    activity_score = calculate_activity_score(patient)
    survey_score = calculate_survey_score(patient)

    return RiskScore(
        value=symptom_score + activity_score + survey_score
    )

def calculate_symptom_score(patient: Patient) -> int:
    score = 0
    if patient.cough_frequency == "often":
        score += 20
    if patient.shortness_of_breath == "severe":
        score += 30
    return score

# ... 其他提取的函數
```

#### 策略 2: Replace Conditional with Polymorphism (多型替換條件)

**適用場景**: 大量 if-elif 判斷不同類型

```python
# Before
def send_notification(notification_type: str, user: User, message: str):
    if notification_type == "line":
        # LINE 推播邏輯
        line_client.push_message(user.line_id, message)
    elif notification_type == "email":
        # Email 邏輯
        smtp.send(user.email, message)
    elif notification_type == "sms":
        # SMS 邏輯
        sms_client.send(user.phone, message)

# After (使用多型)
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user: User, message: str):
        pass

class LINEChannel(NotificationChannel):
    def send(self, user: User, message: str):
        line_client.push_message(user.line_id, message)

class EmailChannel(NotificationChannel):
    def send(self, user: User, message: str):
        smtp.send(user.email, message)

class SMSChannel(NotificationChannel):
    def send(self, user: User, message: str):
        sms_client.send(user.phone, message)

# 使用
channels = {
    "line": LINEChannel(),
    "email": EmailChannel(),
    "sms": SMSChannel()
}

def send_notification(notification_type: str, user: User, message: str):
    channel = channels[notification_type]
    channel.send(user, message)
```

#### 策略 3: Introduce Parameter Object (引入參數物件)

**適用場景**: 函數參數 > 4 個

```python
# Before
def create_patient(
    name: str,
    age: int,
    gender: str,
    phone: str,
    address: str,
    line_id: str,
    copd_stage: str,
    therapist_id: int
):
    # ...

# After
class CreatePatientRequest(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    address: str
    line_id: str
    copd_stage: str
    therapist_id: int

def create_patient(request: CreatePatientRequest):
    # ...
```

---

## 📝 PR Template (Pull Request 模板)

### RespiraAlly PR 標準格式

```markdown
## 📋 變更摘要 (Summary)
<!-- 簡短描述這個 PR 做了什麼 -->

## 🏷️ 變更類型 (Type of Change)
- [ ] 🐛 Bug 修復 (Bug fix)
- [ ] ✨ 新功能 (New feature)
- [ ] 💥 破壞性變更 (Breaking change)
- [ ] 📝 文檔更新 (Documentation update)
- [ ] ♻️ 重構 (Refactoring)
- [ ] 🎨 樣式調整 (Style/UI change)

## 🎯 關聯 Issue
<!-- Closes #123, Fixes #456 -->

## 🔍 變更細節 (Details)
<!-- 詳細說明技術實現、設計決策 -->

## 🧪 測試 (Testing)
- [ ] 單元測試通過 (Unit tests pass)
- [ ] 整合測試通過 (Integration tests pass)
- [ ] 手動測試完成 (Manual testing completed)
- [ ] 測試覆蓋率 ≥ 80%

## ✅ 檢查清單 (Checklist)
- [ ] 代碼符合 Black/Ruff 格式
- [ ] Mypy 類型檢查通過
- [ ] 無循環依賴 (pydeps 檢查)
- [ ] 遵循 Clean Architecture 分層
- [ ] 跨模組調用使用事件
- [ ] 已更新相關文檔
- [ ] Commit Message 符合 Conventional Commits
- [ ] Self-review 完成

## 📸 截圖 (Screenshots)
<!-- 如果是 UI 變更，附上截圖 -->

## 🚀 部署注意事項 (Deployment Notes)
<!-- 數據庫遷移、環境變數變更等 -->
```

---

## 🎯 Quality Gates (品質關卡)

### Before Merge (合併前)

**自動化檢查** (CI Pipeline):
- ✅ Black/Ruff 格式檢查通過
- ✅ Mypy 類型檢查通過
- ✅ Pytest 單元測試通過 (覆蓋率 ≥ 80%)
- ✅ Bandit 安全掃描無 High/Medium 風險
- ✅ Pydeps 循環依賴檢查通過

**人工審查** (Manual Review):
- ✅ 至少 1 位 Peer Reviewer 批准
- ✅ 架構變更需 System Architect 批准
- ✅ 安全相關需 Security Engineer 批准

### Post-Merge (合併後)

**部署驗證**:
- ✅ Staging 環境部署成功
- ✅ Smoke Test 通過 (健康檢查端點)
- ✅ 監控無異常 (Prometheus Alerts)

---

## 📊 技術債管理 (Technical Debt Management)

### 技術債分類

| 類型 | 定義 | 範例 | 償還策略 |
|------|------|------|---------|
| **設計債** | 架構設計不當導致難以擴展 | 模組耦合、違反 SOLID | Sprint 保留 20% 時間重構 |
| **測試債** | 測試覆蓋率不足 | 關鍵業務邏輯無測試 | 新功能必須附帶測試 |
| **文檔債** | 文檔過時或缺失 | API 文檔未更新 | PR 必須更新相關文檔 |
| **依賴債** | 外部依賴版本過舊 | 使用已停止維護的庫 | Dependabot 自動化更新 |

### 技術債追蹤

**GitHub Issues 標籤**:
- `tech-debt:design` - 設計債
- `tech-debt:test` - 測試債
- `tech-debt:docs` - 文檔債
- `tech-debt:dependency` - 依賴債

**優先級**:
- `P0` - 阻塞新功能開發，本 Sprint 必償還
- `P1` - 影響開發效率，下 Sprint 償還
- `P2` - 可容忍，累積 5 個後償還

**償還計畫**:
- 每 Sprint **保留 20% 工時** (約 16-20h) 處理技術債
- Sprint Planning 時檢討技術債累積情況
- Sprint Retrospective 時討論技術債來源

---

## 🔗 相關文檔

- [模組依賴關係分析 (09_module_dependency_analysis.md)](./09_module_dependency_analysis.md)
- [開發流程規範 (01_development_workflow.md)](./01_development_workflow.md)
- [Git Workflow SOP (project_management/git_workflow_sop.md)](./project_management/git_workflow_sop.md)
- [PR Review SLA Policy (project_management/pr_review_sla_policy.md)](./project_management/pr_review_sla_policy.md)

---

**版本記錄**:
- v1.0 (2025-10-19): 初版建立 - Sprint 0 → Sprint 1 轉換期

**審查狀態**: 待 Backend Lead, Tech Lead 審核
**下次更新**: Sprint 1 Week 2 (2025-11-01) - 補充實際 Review 中發現的問題
