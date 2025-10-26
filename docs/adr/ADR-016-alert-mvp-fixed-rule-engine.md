# ADR-016: Alert MVP Strategy - 固定規則引擎 (Fixed Rule Engine)

**狀態**: ✅ 已批准 (Accepted)
**日期**: 2025-10-26
**決策者**: Product Manager, Technical Lead, TaskMaster Hub
**影響範圍**: Alert System, Risk Assessment Integration, Domain Layer
**實作時間**: 12h (Sprint 4 Phase 2)
**相關檔案**:
- `domain/services/alert_rule_engine.py` (AlertRuleEngine with 3 fixed rules)
- `application/alert/alert_service.py` (AlertService)
- `application/risk/use_cases/calculate_risk_use_case.py` (Auto Alert Trigger)
- `api/v1/routers/alert.py` (Alert API endpoints)
- `docs/technical_debt/REGISTRY.md` (DEBT-001: Rule Engine Evolution)

---

## 📋 背景 (Context)

### 問題描述

Sprint 4 需要交付 **Alert System MVP**，用於自動偵測高風險 COPD 病患並通知治療師採取行動。

**核心需求**:
1. **自動觸發**: Risk Assessment 完成後自動評估是否需要產生 Alert
2. **規則驅動**: 基於 GOLD ABE 分組、CAT 分數、惡化頻率等臨床指標
3. **可擴展性**: 未來需支援更多規則、可配置閾值、規則優先順序

**時間壓力**:
- Sprint 4 交付期限：2 週
- Alert System + Exacerbation Management API 同時開發
- 需在有限時間內交付可運作的 MVP

### 技術方案選項

#### 方案 A: 資料庫驅動規則引擎 (Database-Driven Rule Engine)
**優點**:
- ✅ 規則可配置，無需修改程式碼
- ✅ 支援規則優先順序、衝突解決
- ✅ 可在 UI 中管理規則（未來）

**缺點**:
- ❌ 需要設計 Rule Schema (JSON DSL)
- ❌ 需要實作 Rule Parser 和 Evaluator
- ❌ 需要 Rule Management UI (CRUD)
- ❌ 預估開發時間：20-24h (超出 Sprint 4 capacity)

#### 方案 B: 固定規則引擎 (Fixed Rule Engine) - **MVP 策略**
**優點**:
- ✅ 簡單直接，易於理解和測試
- ✅ 開發時間短：4-6h (Domain + Application)
- ✅ 專注於核心業務邏輯驗證
- ✅ 可快速迭代調整規則邏輯

**缺點**:
- ❌ 規則變更需要修改程式碼
- ❌ 不支援規則優先順序、衝突解決
- ❌ 未來需要重構為可配置引擎

---

## 🎯 決策 (Decision)

### 採用方案：**B - 固定規則引擎 (Fixed Rule Engine for MVP)**

**核心設計原則** (Linus Torvalds "Practicality Beats Purity"):
> "I'm a big believer in 'Do one thing and do it well.' The MVP is about validating the alert concept, not building a generic rule engine."

#### 1. MVP 規則定義 (3 Fixed Rules)

```python
class AlertRuleEngine:
    """
    Alert Rule Engine - Evaluate patient risk and generate alerts

    MVP Strategy (DEBT-001):
    - 3 fixed rules hard-coded in this class
    - No database-driven rule configuration
    - No rule priority or conflict resolution

    Rules:
    1. GOLD Group E → HIGH_RISK_DETECTED (CRITICAL severity)
    2. CAT Score >= 20 → HIGH_RISK_DETECTED (HIGH severity)
    3. 3+ exacerbations in 12m → EXACERBATION_RISK (MEDIUM severity)
    """

    async def evaluate(self, risk_assessment: RiskAssessmentModel) -> list[AlertCreate]:
        """Evaluate all rules against patient's risk assessment"""
        alerts: list[AlertCreate] = []

        # Rule 1: GOLD Group E Detection
        if self._is_gold_group_e(risk_assessment):
            alerts.append(self._create_gold_e_alert(risk_assessment))

        # Rule 2: High CAT Score
        if self._is_high_cat_score(risk_assessment):
            alerts.append(self._create_high_cat_alert(risk_assessment))

        # Rule 3: Frequent Exacerbations
        if self._is_frequent_exacerbations(risk_assessment):
            alerts.append(self._create_frequent_exacerbation_alert(risk_assessment))

        return alerts
```

**規則邏輯**:

| Rule ID | 觸發條件 | Alert Type | Severity | 臨床意義 |
|---------|----------|------------|----------|----------|
| GOLD_GROUP_E | `gold_group == "E"` | HIGH_RISK_DETECTED | CRITICAL | 最高風險病患 (≥2 exacerbations OR ≥1 hospitalization) |
| HIGH_CAT_SCORE | `cat_score >= 20` | HIGH_RISK_DETECTED | HIGH | 高症狀負擔 (CAT ≥20 表示症狀嚴重影響生活) |
| FREQUENT_EXACERBATIONS | `exacerbation_count_12m >= 3` | EXACERBATION_RISK | MEDIUM | 頻繁惡化 (預測未來惡化風險) |

#### 2. 自動觸發整合

```python
# application/risk/use_cases/calculate_risk_use_case.py
class CalculateRiskUseCase:
    async def execute(self, patient_id: UUID) -> RiskAssessmentResponse:
        # ... calculate risk assessment ...

        # 自動觸發 Alert 評估 (MVP Auto-Trigger)
        alert_engine = AlertRuleEngine()
        alert_creates = await alert_engine.evaluate(risk_assessment_model)

        if alert_creates:
            alert_service = AlertService(self.db_session)
            for alert_create in alert_creates:
                await alert_service.create_alert(alert_create)

        return risk_assessment_response
```

#### 3. Alert API Endpoints (Read-Only MVP)

```python
# api/v1/routers/alert.py
@router.get("/patients/{patient_id}/alerts", response_model=AlertListResponse)
async def list_patient_alerts(...)

@router.get("/patients/{patient_id}/alerts/active/count", response_model=int)
async def count_active_alerts(...)

@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert_by_id(...)
```

**MVP 限制**:
- ❌ 無 POST /alerts (自動觸發，不支援手動創建)
- ❌ 無 PATCH /alerts/{id}/acknowledge (未來實作)
- ❌ 無 PATCH /alerts/{id}/resolve (未來實作)

#### 4. Technical Debt 追蹤 (DEBT-001)

**DEBT-001: Alert Rule Engine Evolution**

**Current State (MVP)**:
- 3 fixed rules hard-coded in `AlertRuleEngine`
- No rule configuration, priority, or conflict resolution

**Target State (Post-MVP)**:
```python
# Future: Database-Driven Rule Engine
class Rule(BaseModel):
    rule_id: UUID
    name: str
    description: str
    condition: str  # JSON DSL: {"op": "and", "conditions": [...]}
    alert_type: AlertType
    severity: AlertSeverity
    priority: int
    enabled: bool

# alembic/versions/XXX_add_alert_rules_table.py
CREATE TABLE development.alert_rules (
    rule_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    condition JSONB NOT NULL,  -- Rule DSL
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    priority INT DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE
);
```

**Migration Path**:
1. **Phase 1**: Extract rule logic to separate methods (✅ Done in MVP)
2. **Phase 2**: Design Rule DSL (JSON schema)
3. **Phase 3**: Implement Rule Parser and Evaluator
4. **Phase 4**: Migrate hard-coded rules to database
5. **Phase 5**: Build Rule Management UI

**Estimated Effort**: 16-20h (Sprint 5-6)

---

## ✅ 優點 (Pros)

### MVP 交付速度
- **快速實作**: 4-6h 完成 Domain + Application 層
- **簡單測試**: 規則邏輯清晰，易於單元測試
- **專注驗證**: 專注於驗證 Alert 概念，而非建構通用規則引擎

### 程式碼品質
- **Good Taste Design**: 消除特殊情況，所有規則遵循相同模式
- **單一職責**: AlertRuleEngine 只負責規則評估，不處理持久化
- **易於理解**: Hard-coded rules 比 DSL 更直觀

### 業務價值
- **臨床驗證**: 先驗證 3 個核心規則的臨床價值
- **快速迭代**: 規則邏輯調整只需修改程式碼，無需 UI
- **風險控制**: MVP scope 小，降低交付風險

---

## ❌ 缺點 (Cons)

### 靈活性受限
- **規則變更**: 需修改程式碼，需重新部署
- **新增規則**: 需開發新的 `_is_*` 和 `_create_*` 方法
- **規則優先順序**: 無法動態調整規則執行順序

### 技術債務
- **未來重構**: 需要升級為資料庫驅動引擎
- **程式碼重寫**: Rule evaluation 邏輯需重新設計
- **學習成本**: 團隊需學習 Rule DSL 設計

### 可擴展性
- **規則數量**: Hard-coded 方式不適合管理 10+ 規則
- **複雜條件**: 不支援複雜的 AND/OR/NOT 邏輯組合
- **規則衝突**: 無衝突解決機制 (目前允許多個 Alerts 同時觸發)

---

## 🔄 替代方案 (Alternatives Considered)

### 方案 C: 混合方案 (Hybrid - Rule Templates)

**概念**: 使用 Rule Templates 而非完全動態的 DSL

```python
class RuleTemplate(str, Enum):
    THRESHOLD_CHECK = "threshold"  # field >= value
    RANGE_CHECK = "range"          # min <= field <= max
    CATEGORICAL_MATCH = "category" # field in [values]

class Rule(BaseModel):
    template: RuleTemplate
    params: dict  # {"field": "cat_score", "threshold": 20}
```

**評估**:
- ✅ 比完全 DSL 簡單
- ✅ 支援部分動態配置
- ❌ 仍需資料庫 schema 和 UI
- ❌ Template 設計需要額外時間
- ❌ **Result**: 不適合 MVP，推遲至 Sprint 5

---

## 📊 影響分析 (Impact)

### 功能影響
| 功能 | 影響 | 說明 |
|------|------|------|
| Risk Assessment API | ✅ 增強 | 自動產生 Alert，提升臨床價值 |
| Alert API | ✅ 新增 | 3 個 GET endpoints (list, detail, count) |
| Dashboard | ✅ 支援 | 前端可顯示 Alert badge 和列表 |
| Notification System | ⏸️ 延後 | Alert 資料就緒，但通知延後至 Sprint 5+ |

### 性能影響
- **Rule Evaluation**: O(1) 時間複雜度 (3 個固定規則)
- **Database Writes**: 每次 Risk Assessment 最多產生 3 個 Alert records
- **Memory**: 無需載入規則配置，記憶體佔用最小

### 團隊影響
- **開發**: 減少 12-16h 開發時間 (vs 完整 Rule Engine)
- **測試**: 簡化測試複雜度，專注於規則邏輯驗證
- **維護**: 短期內維護成本低，未來需重構投入

---

## 🎓 經驗教訓 (Lessons Learned)

### Linus Torvalds 哲學應用

**"Talk is cheap. Show me the code."**
- MVP 優先交付可運作的程式碼，驗證概念
- 避免過度設計 (Over-engineering)

**"Premature optimization is the root of all evil."**
- 不要在 MVP 階段建構通用 Rule Engine
- 先驗證業務價值，再優化架構

### 技術債務管理

**好的技術債** (Good Technical Debt):
- 有明確的償還計畫 (DEBT-001 in Registry)
- 權衡是有意識的 (Conscious Trade-off)
- 不影響當前交付品質

**壞的技術債** (Bad Technical Debt):
- 無文檔記錄，團隊不知情
- 無償還計畫，永遠拖延
- 影響系統穩定性

---

## 📝 決策驗證標準 (Validation Criteria)

### MVP 成功標準
- [ ] ✅ 3 個規則成功觸發 Alert (已驗證)
- [ ] ✅ Alert API 返回正確資料 (已驗證)
- [ ] ✅ 前端可顯示 Alert 通知 (待前端整合)
- [ ] ✅ 臨床專家確認規則合理性 (待驗證)

### Post-MVP 重構觸發條件
- [ ] 規則數量 > 5 個
- [ ] 需要動態調整規則閾值 (無需部署)
- [ ] 需要規則優先順序和衝突解決
- [ ] 需要 Rule Management UI

---

## 🔗 相關文件 (Related Documents)

- **ADR-013**: COPD Risk Engine Architecture (Risk Assessment 計算邏輯)
- **ADR-014**: GOLD Classification System Adoption (GOLD ABE 分組)
- **ADR-017**: Notification System Deferred (Alert vs Notification 分離)
- **DEBT-001**: Alert Rule Engine Evolution (Technical Debt Registry)
- **EVOLUTION_MAP.md**: Alert System 演進路線圖

---

## 🚀 下一步 (Next Steps)

### Sprint 4 (Current)
- [x] ✅ 實作 AlertRuleEngine (3 fixed rules)
- [x] ✅ 整合至 CalculateRiskUseCase (auto-trigger)
- [x] ✅ 實作 Alert API (read-only endpoints)
- [x] ✅ 手動測試驗證

### Sprint 5 (Post-MVP)
- [ ] 📋 收集臨床專家回饋，調整規則邏輯
- [ ] 📋 實作 Notification System (ADR-017)
- [ ] 📋 Alert acknowledge/resolve endpoints
- [ ] 📋 前端整合 Alert notifications

### Sprint 6+ (Long-term)
- [ ] 🔮 設計 Rule DSL (JSON schema)
- [ ] 🔮 實作 Rule Parser and Evaluator
- [ ] 🔮 Database migration (alert_rules table)
- [ ] 🔮 Rule Management UI

---

**簽核**: TaskMaster Hub Coordination (2025-10-26)
**技術審查**: Linus-Inspired Code Quality Standards Applied ✅
**業務審查**: MVP Scope Validated, Post-MVP Roadmap Defined ✅
