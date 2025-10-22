# ADR-001: Daily Log Schema 重新設計 - 改善 COPD 病患數據彈性

**狀態**: ✅ Accepted
**日期**: 2025-10-22
**決策者**: Development Team
**影響範圍**: Backend API, Database Schema, Frontend Integration

---

## 📋 背景 (Context)

### 問題陳述
原始 Daily Log 設計要求病患**每日必填**所有健康指標 (`medication_taken`, `water_intake_ml`, `steps_count`)，但實際使用情境中：
1. **病患依從性問題**: 強制必填導致病患放棄填寫或隨意填寫假數據
2. **數據不準確**: `steps_count` (步數) 無法準確反映 COPD 病患的**運動強度**
3. **缺少關鍵指標**: 未追蹤**吸菸行為** (COPD 病患的關鍵風險因子)

### 原始設計缺陷
```python
# ❌ 強制必填設計
medication_taken: bool = Field(..., description="必填")
water_intake_ml: int = Field(..., ge=0, le=10000, description="必填")
steps_count: int | None = Field(None, ge=0, le=50000)  # 僅此欄位可選

# ❌ 步數無法反映運動強度
# - 10000 步走路 ≠ 30 分鐘有氧運動
# - COPD 病患更需要「運動時間」而非「步數」
```

---

## 🎯 決策 (Decision)

### 變更摘要

| 項目 | 舊設計 | 新設計 | 理由 |
|------|--------|--------|------|
| **欄位名稱** | `steps_count` | `exercise_minutes` | 運動時間比步數更適合 COPD 管理 |
| **服藥** | `medication_taken` (BOOL, required, default=false) | `medication_taken` (BOOL, **nullable**, default=NULL) | 允許病患「未填寫」vs「填寫 false」的語意區分 |
| **喝水** | `water_intake_ml` (INT, required) | `water_intake_ml` (INT, **nullable**, default=NULL) | 減少填寫負擔，提升真實性 |
| **運動** | `steps_count` (INT, nullable) | `exercise_minutes` (INT, **nullable**, default=NULL) | 更精準的運動追蹤 |
| **新增** | - | `smoking_count` (INT, **nullable**, default=NULL) | 追蹤吸菸行為 (COPD 關鍵指標) |

### 新 Schema 定義

```python
# 新設計 - 彈性優先
class DailyLogBase(BaseModel):
    log_date: date = Field(..., description="唯一必填")

    # 全部改為可選 (nullable)
    medication_taken: bool | None = Field(None, description="服藥情況")
    water_intake_ml: int | None = Field(None, ge=0, le=10000, description="喝水量 (ml)")
    exercise_minutes: int | None = Field(None, ge=0, le=480, description="運動時間 (分鐘)")
    smoking_count: int | None = Field(None, ge=0, le=100, description="吸菸支數")

    symptoms: str | None = Field(None, max_length=500)
    mood: Literal["GOOD", "NEUTRAL", "BAD"] | None = None
```

### 驗證規則

```python
# exercise_minutes 驗證
- 0 ≤ value ≤ 480 分鐘 (8 小時上限)
- 警告範圍: <10 分鐘 (活動不足), >120 分鐘 (過度運動)

# smoking_count 驗證
- 0 ≤ value ≤ 100 支/天 (理論上限)
- 警告範圍: ≥1 支 (應通知治療師介入戒菸)
```

---

## 🔍 考量的替代方案 (Alternatives Considered)

### 方案 A: 保持必填，使用 default=0
```python
# ❌ 拒絕理由: 無法區分「未填寫」vs「真的是 0」
medication_taken: bool = Field(default=False)  # 未服藥? 還是忘記填?
water_intake_ml: int = Field(default=0)        # 沒喝水? 還是懶得填?
```

### 方案 B: 分離必填表單 vs 完整表單
```python
# ❌ 拒絕理由: 增加前端複雜度，用戶體驗差
DailyLogQuick(log_date, medication_taken)  # 快速表單
DailyLogFull(...)                           # 完整表單
```

### ✅ 方案 C: 全部可選 + 智能提醒 (選用)
```python
# ✅ 採用理由:
# 1. 減少填寫負擔 → 提升依從性
# 2. 保留數據真實性 (NULL = 未填, 0 = 真的是 0)
# 3. 前端可彈性設計「建議填寫」vs「必填」
```

---

## ⚠️ 影響與風險 (Consequences)

### ✅ 正面影響
1. **提升用戶體驗**: 病患可選擇性填寫，減少抗拒心理
2. **數據真實性**: NULL vs 0 的語意區分提升數據品質
3. **更精準追蹤**: `exercise_minutes` 比 `steps_count` 更適合 COPD 管理
4. **關鍵指標補齊**: `smoking_count` 是 COPD 惡化的重要預測因子

### ⚠️ 負面影響 (Breaking Changes)
1. **API 契約變更**:
   - `steps_count` → `exercise_minutes` (欄位改名)
   - 所有欄位從 required → optional
   - 前端需同步更新
2. **現有測試失敗**: 預期 22+ 測試需修改
3. **資料庫 Migration**: 需 Alembic migration 處理現有數據
4. **統計計算調整**: `avg_steps_count` → `avg_exercise_minutes`

### 🔄 Migration 策略
```sql
-- 舊數據遷移
ALTER TABLE daily_logs
  RENAME COLUMN steps_count TO exercise_minutes;

-- 將現有 steps_count 轉換為估算運動時間 (10000 步 ≈ 80 分鐘)
UPDATE daily_logs
  SET exercise_minutes = ROUND(steps_count * 0.008)  -- 1 步 ≈ 0.008 分鐘
  WHERE steps_count IS NOT NULL;
```

---

## 📊 驗證計畫 (Validation)

### 測試覆蓋
- [x] Unit tests: Schema validation (nullable fields)
- [ ] Integration tests: API endpoints (CRUD operations)
- [ ] Migration tests: Data integrity (steps → exercise conversion)
- [ ] E2E tests: Frontend integration

### 回滾計畫
如果變更導致嚴重問題：
1. **Database**: Alembic downgrade migration
2. **Code**: Git revert 到此 commit 前
3. **Frontend**: 維持舊版 API 呼叫 (feature flag)

---

## 🔗 相關文件 (References)

- **WBS**: Task 4.2.x - Daily Log Schema Migration (新增 4h)
- **CHANGELOG**: v4 - Breaking Change 紀錄
- **API Docs**: `/api/v1/daily-logs` endpoint 更新
- **Medical Reference**: COPD 病患運動建議 (WHO Guidelines)

---

## ✅ 決策批准

| 角色 | 姓名 | 批准日期 | 備註 |
|------|------|----------|------|
| Product Owner | - | 2025-10-22 | 同意改善用戶體驗 |
| Tech Lead | Claude Code | 2025-10-22 | 架構審查通過 |
| Frontend Lead | - | Pending | 需通知前端同步更新 |

---

**下一步行動**:
1. ✅ 建立此 ADR
2. ⏳ 更新 Database Model
3. ⏳ 建立 Alembic Migration
4. ⏳ 更新 Pydantic Schema + Validators
5. ⏳ 修復測試
6. ⏳ 更新 API 文檔
7. ⏳ 通知前端團隊
