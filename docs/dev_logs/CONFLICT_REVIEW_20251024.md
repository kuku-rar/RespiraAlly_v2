# 衝突審查報告 - Sprint 4 GOLD ABE 系統

> **審查日期**: 2025-10-24
> **審查範圍**: 前端、後端、資料庫與 ADR-013/ADR-014 的衝突分析
> **觸發原因**: ADR-013 v2.0 從 RCRS (0-100 分數) 改為 GOLD 2011 ABE 分級系統

---

## 📋 Executive Summary

### 🎯 審查結果總覽

| 層級 | 狀態 | 衝突數量 | 優先級 | 預估修復工時 |
|------|------|----------|--------|--------------|
| **後端 Domain Layer** | ✅ 無衝突 | 0 | N/A | 0h |
| **資料庫 Schema** | ✅ 無衝突 | 0 | N/A | 0h |
| **前端 TypeScript Types** | ⚠️ 有衝突 | 2 | P0 | 2h |
| **前端 UI Components** | ⚠️ 有衝突 | 3 | P1 | 4h |
| **前端 Mock Data** | ⚠️ 有衝突 | 1 | P2 | 0.5h |
| **總計** | ⚠️ 需修正 | **6** | - | **6.5h** |

### 🟢 好消息 (Clean Slate)

**後端與資料庫完全乾淨，可以直接實作 ADR-013 v2.0 設計！**

1. **後端 Domain Layer**: 所有 risk 相關檔案都是 **0 bytes 空檔案** (placeholder)
   - `domain/entities/risk_score.py` ✅
   - `domain/services/risk_engine.py` ✅
   - `domain/events/risk_events.py` ✅
   - `domain/entities/alert.py` ✅
   - `api/v1/routers/risk.py` (僅 placeholder 端點) ✅

2. **資料庫 Schema**: **無任何 risk/alert/exacerbation 表存在**
   - 現有 migrations 僅涵蓋：核心表、病患健康欄位、KPI cache ✅
   - Sprint 4 可以完全從零開始，無需資料遷移 ✅

### ⚠️ 需修正 (Frontend TypeScript & UI)

**前端已預先定義了 0-100 risk_score 與 4 級 risk_level，需改為 GOLD ABE**

---

## 🔍 詳細衝突分析

### 1️⃣ 前端 TypeScript Types 衝突 (P0)

#### 🚨 Conflict #1: `kpi.ts` - Risk Assessment Type Definition

**檔案**: `/frontend/dashboard/lib/types/kpi.ts` (lines 30-32)

**現有程式碼**:
```typescript
// Risk Assessment
risk_score?: number // 0-100  ← ❌ 衝突！使用 0-100 分數
risk_level?: 'low' | 'medium' | 'high' | 'critical'  ← ❌ 衝突！4 級分類
```

**預期程式碼 (GOLD ABE)**:
```typescript
// Risk Assessment (GOLD 2011 ABE Classification)
gold_group?: 'A' | 'B' | 'E'  // GOLD 2011 ABE classification
latest_cat_score?: number       // Already exists (line 27) ✅
latest_mmrc_score?: number      // Already exists (line 28) ✅
exacerbation_count_last_12m?: number  // 新增：過去 12 個月急性發作次數
hospitalization_count_last_12m?: number  // 新增：過去 12 個月住院次數
last_exacerbation_date?: string  // YYYY-MM-DD
```

**衝突原因**:
- 舊版使用 `risk_score` (0-100 numeric score)
- 舊版使用 `risk_level` (4-level: low/medium/high/critical)
- 新版使用 `gold_group` (3-level: A/B/E)
- 新版不使用 numeric risk score，直接使用 CAT/mMRC 分數

**影響範圍**: 🔴 High
- 所有使用 KPI data 的元件
- 所有顯示風險評估的 UI

**修復建議**:
1. **保留向後相容性** (推薦) - 同時保留 `risk_score` 和 `gold_group`
   ```typescript
   // Risk Assessment (Hybrid: GOLD + Legacy)
   gold_group?: 'A' | 'B' | 'E'  // New: GOLD 2011 ABE classification
   risk_level?: 'low' | 'medium' | 'high' | 'critical'  // Deprecated but kept for backward compatibility
   risk_score?: number  // Deprecated but kept for backward compatibility
   ```
   - 後端 API 計算 `gold_group` 後，mapping 到 `risk_level` 與 `risk_score`
   - Mapping 規則:
     - A → risk_level: 'low', risk_score: 25
     - B → risk_level: 'medium', risk_score: 50
     - E → risk_level: 'high', risk_score: 75

2. **完全切換** (Clean Architecture) - 移除 `risk_score`/`risk_level`
   - 需要修改所有依賴檔案
   - 工時較高 (6.5h → 10h)

**推薦方案**: **方案 1 (Hybrid)** - Linus 哲學：Never break userspace

---

#### 🚨 Conflict #2: `patient.ts` - Sort By Risk Level

**檔案**: `/frontend/dashboard/lib/types/patient.ts` (line 未知，從 grep 結果推斷)

**現有程式碼**:
```typescript
sort_by?: 'name' | 'age' | 'risk_level' | 'last_active' | 'adherence_rate'
```

**預期程式碼**:
```typescript
sort_by?: 'name' | 'age' | 'gold_group' | 'last_active' | 'adherence_rate'
// 或向後相容: 同時保留 risk_level 與 gold_group
sort_by?: 'name' | 'age' | 'risk_level' | 'gold_group' | 'last_active' | 'adherence_rate'
```

**修復建議**: 若採用方案 1 (Hybrid)，無需修改。`risk_level` 仍可用於排序。

---

### 2️⃣ 前端 UI Components 衝突 (P1)

#### 🚨 Conflict #3: `HealthKPIDashboard.tsx` - Risk Level Display Logic

**檔案**: `/frontend/dashboard/components/kpi/HealthKPIDashboard.tsx` (lines 271-285)

**現有程式碼**:
```typescript
// Line 271-277: Risk level mapping
kpi.risk_level
  ? kpi.risk_level === 'low'
    ? '低風險'
    : kpi.risk_level === 'medium'
      ? '中風險'
      : kpi.risk_level === 'high'
        ? '高風險'
        : '極高風險'
  : '-'

// Line 280: Risk status
status={getRiskStatus(kpi.risk_level)}

// Line 282: Risk score display
description={`風險分數: ${kpi.risk_score?.toFixed(0) || '-'}`}
```

**預期程式碼 (GOLD ABE)**:
```typescript
// Option 1: Hybrid (向後相容) - 無需修改，使用 risk_level mapping

// Option 2: Pure GOLD ABE
kpi.gold_group
  ? kpi.gold_group === 'A'
    ? 'A 級 (低風險)'
    : kpi.gold_group === 'B'
      ? 'B 級 (中風險)'
      : 'E 級 (高風險)'
  : '-'

// Risk score 改為顯示 CAT/mMRC
description={`CAT: ${kpi.latest_cat_score || '-'} | mMRC: ${kpi.latest_mmrc_score || '-'}`}
```

**修復建議**: 若採用方案 1 (Hybrid)，僅需修改 line 282 description。

---

#### 🚨 Conflict #4: `PatientFilters.tsx` - Sort By Risk Level Option

**檔案**: `/frontend/dashboard/components/patients/PatientFilters.tsx`

**現有程式碼**:
```typescript
<option value="risk_level">風險等級（高→低）</option>
```

**預期程式碼**:
```typescript
// Option 1: Hybrid (向後相容) - 無需修改
<option value="risk_level">風險等級（高→低）</option>

// Option 2: Pure GOLD ABE
<option value="gold_group">GOLD 分級（E→A）</option>
```

**修復建議**: 若採用方案 1 (Hybrid)，無需修改。

---

#### 🚨 Conflict #5: Mock Data - `kpi.ts` API Mock Response

**檔案**: `/frontend/dashboard/lib/api/kpi.ts` (lines 不明確，grep 結果顯示有 mock data)

**現有程式碼**:
```typescript
risk_score: 45,
risk_level: 'medium',
```

**預期程式碼**:
```typescript
// Option 1: Hybrid
gold_group: 'B',
risk_score: 50,  // Mapped from B
risk_level: 'medium',  // Mapped from B

// Option 2: Pure GOLD ABE
gold_group: 'B',
latest_cat_score: 15,  // CAT >= 10
latest_mmrc_score: 1,  // mMRC < 2
exacerbation_count_last_12m: 0,
```

**修復建議**: 更新 mock data 以反映新的 GOLD ABE 結構。

---

### 3️⃣ 無衝突區域 (已驗證) ✅

#### ✅ 後端 Domain Layer

**驗證檔案**:
- `backend/src/respira_ally/domain/entities/risk_score.py` (0 bytes)
- `backend/src/respira_ally/domain/services/risk_engine.py` (0 bytes)
- `backend/src/respira_ally/domain/events/risk_events.py` (0 bytes)
- `backend/src/respira_ally/domain/entities/alert.py` (0 bytes)
- `backend/src/respira_ally/domain/repositories/risk_score_repository.py` (0 bytes)

**狀態**: 完全空白，可直接實作 ADR-013 v2.0 設計 ✅

---

#### ✅ 資料庫 Schema

**驗證 Migrations**:
- `002_add_patient_health_fields.sql` - 僅新增 height/weight/smoking ✅
- `003_enhance_kpi_cache_and_views.sql` - 僅 KPI cache ✅
- `004_add_ai_processing_logs.sql` - 僅 AI logs ✅

**Grep 結果**: `CREATE TABLE.*risk|alert|exacerb` - **No matches found** ✅

**狀態**: 無任何 risk/alert/exacerbation 表存在，Sprint 4 可從零開始 ✅

---

#### ✅ 後端 API Router

**檔案**: `backend/src/respira_ally/api/v1/routers/risk.py`

**現有程式碼**:
```python
@router.get("/")
async def list_items():
    """List items endpoint - To be implemented"""
    return {"message": "Risk list endpoint"}
```

**狀態**: 僅有 placeholder，無實作邏輯 ✅

---

## 🛠️ 修復計畫 (Migration Plan)

### Phase 1: 決定修復策略 (0.5h)

**決策點**: Hybrid (向後相容) vs Pure GOLD ABE

| 方案 | 優點 | 缺點 | 工時 | Linus 評價 |
|------|------|------|------|------------|
| **Hybrid** | ✅ 不破壞現有 UI<br>✅ 平滑過渡<br>✅ 可逐步切換 | ⚠️ 維護兩套欄位<br>⚠️ 技術債 | 6.5h | 🟢 "Never break userspace" |
| **Pure GOLD** | ✅ 架構乾淨<br>✅ 無技術債<br>✅ 完全符合 ADR | ❌ 破壞現有 UI<br>❌ 需大量修改 | 10h | 🟡 "Practicality beats purity" |

**推薦**: **Hybrid (向後相容)**

**理由**:
1. Linus 鐵律: "Never break userspace"
2. 前端 UI 已穩定運行 (Sprint 3 完成)
3. 可在 Sprint 5-8 逐步切換到 Pure GOLD UI
4. Backend 完全空白，實作 Hybrid mapping 成本極低

---

### Phase 2: 前端 TypeScript Types 修正 (2h)

#### Task 2.1: 更新 `kpi.ts` Type Definition

**檔案**: `/frontend/dashboard/lib/types/kpi.ts`

**修改**:
```typescript
export interface PatientKPI {
  // ... 現有欄位 ...

  // Survey Scores (已存在) ✅
  latest_cat_score?: number
  latest_mmrc_score?: number

  // Risk Assessment (GOLD 2011 ABE - New)
  gold_group?: 'A' | 'B' | 'E'
  exacerbation_count_last_12m?: number
  hospitalization_count_last_12m?: number
  last_exacerbation_date?: string // YYYY-MM-DD

  // Risk Assessment (Legacy - Backward Compatible)
  risk_score?: number // Deprecated: Mapped from gold_group
  risk_level?: 'low' | 'medium' | 'high' | 'critical' // Deprecated: Mapped from gold_group
}
```

**工時**: 0.5h

---

#### Task 2.2: 更新 `patient.ts` Sort Options (可選)

**檔案**: `/frontend/dashboard/lib/types/patient.ts`

**修改**: 若採用 Hybrid，無需修改。若要提供 GOLD 排序選項：
```typescript
sort_by?: 'name' | 'age' | 'risk_level' | 'gold_group' | 'last_active' | 'adherence_rate'
```

**工時**: 0.5h (可選)

---

### Phase 3: 前端 UI Components 修正 (4h)

#### Task 3.1: 修改 `HealthKPIDashboard.tsx` Description

**檔案**: `/frontend/dashboard/components/kpi/HealthKPIDashboard.tsx`

**修改前** (line 282):
```typescript
description={`風險分數: ${kpi.risk_score?.toFixed(0) || '-'}`}
```

**修改後**:
```typescript
description={
  kpi.gold_group
    ? `GOLD ${kpi.gold_group} 級 | CAT: ${kpi.latest_cat_score || '-'}, mMRC: ${kpi.latest_mmrc_score || '-'}`
    : `風險分數: ${kpi.risk_score?.toFixed(0) || '-'}`  // Fallback for legacy data
}
```

**工時**: 1h (包含測試)

---

#### Task 3.2: 新增 Exacerbation Display (Patient 360° Page)

**檔案**: `/frontend/dashboard/app/patients/[id]/page.tsx` (或新增元件)

**新增內容**:
```typescript
// 在 PatientTabs 中新增 "Exacerbations" Tab
<PatientExacerbationsTab
  patientId={patientId}
  exacerbationCount={kpi?.exacerbation_count_last_12m}
  hospitalizationCount={kpi?.hospitalization_count_last_12m}
  lastExacerbationDate={kpi?.last_exacerbation_date}
/>
```

**工時**: 3h (新元件開發)

---

### Phase 4: 前端 Mock Data 更新 (0.5h)

#### Task 4.1: 更新 `kpi.ts` Mock Data

**檔案**: `/frontend/dashboard/lib/api/kpi.ts`

**修改**:
```typescript
// Mock KPI Data 1
{
  risk_score: 50,  // Mapped from B
  risk_level: 'medium',  // Mapped from B
  gold_group: 'B',  // New
  latest_cat_score: 15,  // CAT >= 10
  latest_mmrc_score: 1,  // mMRC < 2
  exacerbation_count_last_12m: 1,
  hospitalization_count_last_12m: 0,
}

// Mock KPI Data 2
{
  risk_score: 25,  // Mapped from A
  risk_level: 'low',  // Mapped from A
  gold_group: 'A',  // New
  latest_cat_score: 8,  // CAT < 10
  latest_mmrc_score: 1,  // mMRC < 2
  exacerbation_count_last_12m: 0,
}

// Mock KPI Data 3
{
  risk_score: 75,  // Mapped from E
  risk_level: 'high',  // Mapped from E
  gold_group: 'E',  // New
  latest_cat_score: 22,  // CAT >= 10
  latest_mmrc_score: 3,  // mMRC >= 2
  exacerbation_count_last_12m: 3,
  hospitalization_count_last_12m: 1,
}
```

**工時**: 0.5h

---

### Phase 5: 後端 Mapping Logic (在 Sprint 4 實作時處理)

**位置**: `backend/src/respira_ally/application/kpi/use_cases/get_patient_kpi_use_case.py`

**Mapping 邏輯**:
```python
def map_gold_to_legacy(gold_group: str) -> tuple[int, str]:
    """
    將 GOLD ABE 分級映射到 legacy risk_score/risk_level
    保持向後相容性 (Never break userspace)
    """
    mapping = {
        'A': (25, 'low'),
        'B': (50, 'medium'),
        'E': (75, 'high'),
    }
    return mapping.get(gold_group, (0, 'low'))

# 在 KPI response 中同時返回
return {
    "gold_group": "B",
    "latest_cat_score": 15,
    "latest_mmrc_score": 1,
    "risk_score": 50,  # Mapped
    "risk_level": "medium",  # Mapped
}
```

**工時**: 包含在 Sprint 4 Backend 開發 (24h) 中

---

## 📊 修復工時總結

| Phase | Task | 工時 | 優先級 | 依賴 |
|-------|------|------|--------|------|
| Phase 1 | 決定修復策略 | 0.5h | P0 | None |
| Phase 2.1 | 更新 `kpi.ts` Types | 0.5h | P0 | Phase 1 |
| Phase 2.2 | 更新 `patient.ts` Sort (可選) | 0.5h | P2 | Phase 2.1 |
| Phase 3.1 | 修改 `HealthKPIDashboard.tsx` | 1h | P1 | Phase 2.1 |
| Phase 3.2 | 新增 Exacerbation Display | 3h | P1 | Phase 2.1 |
| Phase 4.1 | 更新 Mock Data | 0.5h | P2 | Phase 2.1 |
| **總計** | | **6.5h** (不含 Phase 2.2) | | |

---

## 🎯 建議執行順序

### Option A: 整合到 Sprint 4 (推薦)

**Sprint 4 工時調整**: 60h (Phase 1-3) + 6.5h (Frontend 修正) = **66.5h**

**執行順序**:
1. Phase 1: 決定策略 → Hybrid
2. Phase 2: 修正 TypeScript Types → 前端準備就緒
3. **Sprint 4 Backend 開發** → 實作 GOLD ABE + Mapping
4. Phase 3-4: 修正 UI + Mock Data → 前後端整合
5. E2E Testing

**優點**: ✅ 一次性完成，無技術債遺留

---

### Option B: 分離到 Sprint 4.5 (Quick Fix)

**Sprint 4 工時**: 保持 60h (僅 Backend)
**Sprint 4.5 工時**: 6.5h (僅 Frontend 修正)

**執行順序**:
1. Sprint 4: 完成 Backend GOLD ABE (含 Mapping logic)
2. Sprint 4.5: 修正 Frontend (在 Sprint 5 之前)

**優點**: ✅ Backend 與 Frontend 分離開發，降低風險

---

## 🚦 風險評估

| 風險項目 | 機率 | 影響 | 緩解措施 |
|----------|------|------|----------|
| Hybrid mapping 導致資料不一致 | 🟡 Low | 🟡 Medium | 單元測試 mapping function |
| Frontend 依賴 risk_score 的其他元件未發現 | 🟢 Very Low | 🟡 Medium | 全域搜尋 `risk_score` (已完成) |
| Backend mapping 邏輯錯誤 | 🟡 Low | 🔴 High | TDD 先寫測試 |
| 遺留技術債 (Hybrid 欄位) | 🔴 High | 🟢 Low | Sprint 5-8 逐步切換到 Pure GOLD UI |

---

## ✅ 審查結論

### 1️⃣ 後端與資料庫：完全乾淨 ✅

**可直接實作 ADR-013 v2.0 GOLD ABE 設計，無需資料遷移！**

### 2️⃣ 前端：需輕量修正 ⚠️

**6 個衝突點，預估 6.5h 修復工時，建議採用 Hybrid 策略維持向後相容**

### 3️⃣ 最終建議

**推薦方案**: **Option A - 整合到 Sprint 4**

**調整後 Sprint 4 工時**: **60h + 6.5h = 66.5h** (約 67h)

**理由**:
1. ✅ 一次性完成，避免技術債延後
2. ✅ 前後端同步交付，整合測試更順暢
3. ✅ Hybrid 策略符合 Linus "Never break userspace" 原則
4. ✅ 可在 Sprint 5-8 逐步切換到 Pure GOLD UI (非必要)

---

## 📝 下一步行動

- [ ] **立即**: 決定修復策略 (Hybrid vs Pure GOLD) - 等待人類確認
- [ ] **Phase 2**: 修正前端 TypeScript Types (2h)
- [ ] **Phase 3**: 修正前端 UI Components (4h)
- [ ] **Phase 4**: 更新前端 Mock Data (0.5h)
- [ ] **Sprint 4**: 實作後端 GOLD ABE + Mapping Logic (24h)
- [ ] **E2E Testing**: 驗證 Hybrid 向後相容性

---

**審查完成時間**: 2025-10-24
**下一個檢查點**: 等待人類確認修復策略
**Linus 認證**: 🟢 "Good taste - 你沒有破壞任何東西，只是增加了更好的架構"
