# Sprint 1-3 技術債與代碼品質審查報告

> **審查日期**: 2025-10-23
> **審查範圍**: Sprint 1-3 所有交付程式碼
> **審查人員**: Claude Code (TaskMaster Hub - Code Quality Specialist)
> **審查標準**: Code Review Guide (11) + Security Checklist (13)

---

## 📊 執行摘要 (Executive Summary)

### 整體評估

**代碼品質成熟度**: 🟡 **中等 (Medium)** - 需要改善

| 類別 | 評分 | 狀態 |
|-----|------|------|
| **代碼格式化** | 🔴 36% | 61/168 檔案需重新格式化 |
| **代碼品質** | 🟡 中 | 174 個 Ruff 錯誤 |
| **類型安全** | 🔴 低 | Mypy 模組衝突 + 大量 Optional 使用 |
| **測試覆蓋率** | 🔴 0% | 測試檔案語法錯誤,無法執行 |
| **安全性** | 🟡 中 | 1 個中危漏洞 (B104) |
| **前端品質** | 🟡 中 | Dashboard: 8 errors, LIFF: 無 ESLint |

**關鍵發現**:
- ✅ **架構設計良好**: Clean Architecture 分層清晰
- ⚠️ **代碼格式未統一**: 大量檔案需 Black 格式化
- ❌ **測試完全失效**: 編碼錯誤導致測試無法執行
- ⚠️ **類型安全不足**: Mypy 模組衝突 + 舊式類型註解
- ⚠️ **前端配置缺失**: LIFF 無 ESLint 配置

---

## 🐛 發現的問題分類 (Issues Classification)

### A. 後端 (Backend) - 109 個問題

#### A.1 代碼格式化 (Black) - **61 檔案**

**嚴重性**: 🟡 Medium (影響代碼可讀性與一致性)

**問題描述**:
- 61/168 檔案 (36%) 不符合 Black 格式標準
- 主要問題: 縮排不一致、換行規則、空格使用

**範例檔案**:
```
src/respira_ally/api/v1/routers/risk.py
src/respira_ally/api/v1/routers/auth.py
src/respira_ally/application/auth/use_cases/login_use_case.py
src/respira_ally/core/config.py
src/respira_ally/main.py
... (共 61 個檔案)
```

**修復方法**:
```bash
cd backend/
uv run black src/
```

**優先級**: **P1** (下次 Sprint 修復)
**預估工時**: 0.5h (自動化修復)

---

#### A.2 代碼品質 (Ruff) - **174 個錯誤**

**嚴重性**: 🟡 Medium to High

**問題分類**:

| 錯誤類型 | 數量 | 嚴重性 | 自動修復 |
|---------|------|--------|----------|
| **I001**: Import 排序問題 | ~50 | Low | ✅ |
| **F401**: 未使用的 import | ~20 | Low | ✅ |
| **B904**: 異常處理缺少 `from` | ~15 | Medium | ✅ |
| **B008**: Query 參數預設值調用 | ~25 | Medium | ❌ |
| **UP045**: 使用 `Optional[X]` 而非 `X \| None` | ~50 | Low | ✅ |
| **UP017**: 使用 `timezone.utc` 而非 `datetime.UTC` | ~5 | Low | ✅ |
| **UP035**: 從 `typing` 匯入而非 `collections.abc` | ~5 | Low | ✅ |

**關鍵問題範例**:

**1. Import 排序問題 (I001)**
```python
# ❌ 錯誤 (src/respira_ally/api/v1/routers/daily_log.py:13)
from typing import Annotated
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends

# ✅ 正確
from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
```

**2. 異常處理問題 (B904)**
```python
# ❌ 錯誤 (src/respira_ally/api/v1/routers/daily_log.py:99)
try:
    ...
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e),
    )

# ✅ 正確
try:
    ...
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e),
    ) from e  # 保留原始異常鏈
```

**3. Query 參數預設值問題 (B008)**
```python
# ❌ 錯誤 (FastAPI 特性,實際可接受但 Ruff 報錯)
async def list_logs(
    patient_id: UUID | None = Query(None, description="Filter by patient ID"),
    start_date: date | None = Query(None, description="Start date"),
):
    ...

# ✅ 建議 (但會失去 OpenAPI 文檔)
async def list_logs(
    patient_id: Annotated[UUID | None, Query(description="Filter by patient ID")] = None,
    start_date: Annotated[date | None, Query(description="Start date")] = None,
):
    ...
```

**修復方法**:
```bash
# 自動修復 139 個問題
uv run ruff check src/ --fix

# 手動修復 B008 (需評估是否真的需要修復)
```

**優先級**: **P0/P1**
- P0 (立即): B904 (異常處理) - 影響除錯
- P1 (下 Sprint): I001, F401, UP045 (格式化問題)

**預估工時**: 2h (自動修復 + 手動審查)

---

#### A.3 類型安全 (Mypy) - **模組衝突 + 大量 Optional**

**嚴重性**: 🔴 High (阻塞 Mypy 執行)

**問題 1: 模組名稱衝突**

```
src/respira_ally/infrastructure/repositories/__init__.py: error:
Duplicate module named "repositories"
(also at "src/respira_ally/domain/repositories/__init__.py")
```

**根本原因**:
- `domain/repositories/` (抽象介面)
- `infrastructure/repositories/` (具體實現)
- Python import system 無法區分同名模組

**解決方案** (三選一):

1. **重命名 infrastructure 模組** (推薦):
   ```
   infrastructure/repositories/ → infrastructure/repository_impls/
   ```

2. **使用 namespace package**:
   ```python
   # domain/repositories/__init__.py
   __path__ = __import__('pkgutil').extend_path(__path__, __name__)
   ```

3. **Mypy 配置排除**:
   ```toml
   [tool.mypy]
   exclude = ["infrastructure/repositories/"]
   ```

**優先級**: **P0** (立即修復,阻塞 CI/CD 類型檢查)
**預估工時**: 1h (重命名 + 更新 import)

---

**問題 2: 舊式 Optional 使用**

Ruff 已識別 ~50 處使用 `Optional[X]` 而非 `X | None`:

```python
# ❌ 舊式 (Python 3.9)
from typing import Optional

def get_patient(id: UUID) -> Optional[PatientModel]:
    ...

# ✅ 新式 (Python 3.10+)
def get_patient(id: UUID) -> PatientModel | None:
    ...
```

**修復方法**:
```bash
uv run ruff check src/ --select UP045 --fix
```

**優先級**: **P1** (下 Sprint)
**預估工時**: 0.5h (自動修復)

---

#### A.4 測試覆蓋率 (Pytest) - **0% (無法執行)**

**嚴重性**: 🔴 Critical (測試完全失效)

**問題**: 測試檔案語法錯誤

```python
# tests/integration/database/test_patient_repository.py:308
update_data = {
    "name": "����W",  # ← 編碼錯誤!
    "height_cm": 175,
}
```

**根本原因**:
- 檔案編碼問題 (UTF-8 BOM 或錯誤字元)
- Line 308, 319 包含亂碼字元

**解決方案**:
1. 修正測試檔案編碼:
   ```python
   # 應改為:
   update_data = {
       "name": "張小明",  # 或其他有效的測試資料
       "height_cm": 175,
   }
   ```

2. 重新執行測試:
   ```bash
   uv run pytest --cov=src/respira_ally --cov-report=term-missing
   ```

**優先級**: **P0** (Critical - 阻塞品質驗證)
**預估工時**: 0.5h (修正編碼 + 執行測試)

---

#### A.5 安全性 (Bandit) - **1 個中危,5 個低危**

**嚴重性**: 🟡 Medium

**中危問題 (B104)**:

```python
# src/respira_ally/main.py:159
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # ← 綁定所有介面
```

**風險**: 允許外部網路直接訪問 (應僅綁定 localhost)

**解決方案**:
```python
# ✅ 開發環境綁定 localhost
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# 生產環境使用 Dockerfile + uvicorn CLI
# CMD ["uvicorn", "respira_ally.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**優先級**: **P1** (下 Sprint 修復)
**預估工時**: 0.5h

---

**低危問題 (B106)**: Hardcoded password (誤報)

```python
# 5 處誤報: token_type="bearer" 不是真的密碼
token_response = TokenResponse(
    access_token=access_token,
    refresh_token=refresh_token,
    token_type="bearer",  # ← Bandit 誤報
)
```

**解決方案**:
```python
# 添加 Bandit 忽略註解
token_type="bearer",  # nosec B106
```

**優先級**: **P2** (低優先級)
**預估工時**: 0.5h

---

### B. 前端 (Frontend) - **10+ 個問題**

#### B.1 Dashboard (Next.js + TypeScript) - **8 errors + 2 warnings**

**嚴重性**: 🟡 Medium

**問題分類**:

| 問題類型 | 數量 | 檔案 |
|---------|------|------|
| **未使用的變數** | 2 | `app/patients/[id]/page.tsx` |
| **any 類型使用** | 6 | `components/health-timeline/*.tsx` |
| **React Hook 依賴** | 2 | `app/patients/page.tsx`, `components/kpi/HealthKPIDashboard.tsx` |

**關鍵問題**:

**1. 未使用的變數 (Error)**
```typescript
// app/patients/[id]/page.tsx:34,43
const { data: logs, isLoading: logsLoading, error: logsError } = useQuery(...);
// ❌ logsError 從未使用

// ✅ 修復: 使用或移除
const { data: logs, isLoading: logsLoading } = useQuery(...);
// 或使用 error:
if (logsError) { ... }
```

**2. any 類型使用 (Error)**
```typescript
// components/health-timeline/ExerciseBarChart.tsx:77
<YAxis tick={(props: any) => <CustomTick {...props} />} />
//              ^^^^ 應定義具體類型

// ✅ 修復:
interface TickProps {
  x: number;
  y: number;
  payload: { value: string };
}
<YAxis tick={(props: TickProps) => <CustomTick {...props} />} />
```

**3. React Hook 依賴警告 (Warning)**
```typescript
// app/patients/page.tsx:43
useEffect(() => {
  fetchPatients();
}, []); // ← 缺少 fetchPatients 依賴

// ✅ 修復 (使用 useCallback):
const fetchPatients = useCallback(async () => { ... }, []);
useEffect(() => {
  fetchPatients();
}, [fetchPatients]);
```

**修復方法**:
```bash
cd frontend/dashboard
npm run lint --fix  # 自動修復部分問題
```

**優先級**: **P1** (下 Sprint)
**預估工時**: 2h (修復所有問題)

---

#### B.2 LIFF (React + TypeScript) - **缺少 ESLint 配置**

**嚴重性**: 🟡 Medium (無法進行代碼品質檢查)

**問題**:
```bash
$ npm run lint
ESLint couldn't find a configuration file.
```

**解決方案**:

1. **初始化 ESLint 配置**:
   ```bash
   cd frontend/liff
   npm init @eslint/config
   ```

2. **使用與 Dashboard 相同的配置**:
   ```bash
   cp ../dashboard/.eslintrc.json .
   cp ../dashboard/.eslintignore .
   ```

3. **調整 package.json**:
   ```json
   {
     "scripts": {
       "lint": "eslint . --ext ts,tsx --max-warnings 0"
     }
   }
   ```

4. **執行 linting**:
   ```bash
   npm run lint
   ```

**優先級**: **P0** (立即設定,阻塞代碼品質檢查)
**預估工時**: 1h (設定 + 修復發現的問題)

---

## 📋 技術債清單與修復計畫

### P0 (Critical) - **立即修復** (Sprint 4 Week 1)

| # | 問題 | 檔案/位置 | 影響 | 工時 |
|:-:|:-----|:---------|:-----|:----:|
| P0-1 | **測試檔案編碼錯誤** | `tests/integration/database/test_patient_repository.py:308` | 測試完全失效 | 0.5h |
| P0-2 | **Mypy 模組衝突** | `domain/repositories/` vs `infrastructure/repositories/` | 阻塞類型檢查 | 1h |
| P0-3 | **LIFF 缺少 ESLint** | `frontend/liff/` | 無法品質檢查 | 1h |
| **小計** | | | | **2.5h** |

---

### P1 (High) - **下個 Sprint 修復** (Sprint 4 Week 2)

| # | 問題 | 檔案/位置 | 影響 | 工時 |
|:-:|:-----|:---------|:-----|:----:|
| P1-1 | **代碼格式化** | 61 個檔案需 Black 格式化 | 可讀性 | 0.5h |
| P1-2 | **Ruff 代碼品質** | 174 個錯誤 (139 個可自動修復) | 代碼品質 | 2h |
| P1-3 | **異常處理缺少 from** | B904 錯誤 (~15 處) | 除錯困難 | 1h |
| P1-4 | **安全性: 綁定所有介面** | `main.py:159` | 安全風險 | 0.5h |
| P1-5 | **Dashboard ESLint 問題** | 8 errors + 2 warnings | 類型安全 | 2h |
| **小計** | | | | **6h** |

---

### P2 (Low) - **技術債累積後修復** (Sprint 11)

| # | 問題 | 檔案/位置 | 影響 | 工時 |
|:-:|:-----|:---------|:-----|:----:|
| P2-1 | **舊式 Optional 使用** | ~50 處 `Optional[X]` | 代碼現代化 | 0.5h |
| P2-2 | **Bandit 誤報** | 5 處 `token_type="bearer"` | 掃描噪音 | 0.5h |
| P2-3 | **Import 排序** | ~50 處 I001 錯誤 | 代碼一致性 | 0.5h |
| **小計** | | | | **1.5h** |

---

### 修復時程規劃

```
Sprint 4 Week 1 (2025-10-28 ~ 11-01):
- P0-1: 測試編碼修復 ✅
- P0-2: Mypy 模組重構 ✅
- P0-3: LIFF ESLint 設定 ✅

Sprint 4 Week 2 (2025-11-04 ~ 11-08):
- P1-1: Black 格式化 ✅
- P1-2: Ruff 自動修復 ✅
- P1-3: 異常處理改善 ✅
- P1-4: 安全性修復 ✅
- P1-5: Dashboard ESLint ✅

Sprint 11 (重構 Sprint):
- P2-1: 類型註解現代化 ✅
- P2-2: Bandit 配置優化 ✅
- P2-3: Import 排序統一 ✅
```

**總工時預估**: **10h** (P0: 2.5h, P1: 6h, P2: 1.5h)

---

## 🎯 建議行動 (Recommended Actions)

### 立即行動 (本週內)

1. **修復測試檔案**:
   ```bash
   # 編輯 tests/integration/database/test_patient_repository.py:308
   # 將 "����W" 改為有效的測試資料 "張小明"
   ```

2. **重命名 infrastructure/repositories**:
   ```bash
   git mv src/respira_ally/infrastructure/repositories \
          src/respira_ally/infrastructure/repository_impls
   # 更新所有 import 引用
   ```

3. **設定 LIFF ESLint**:
   ```bash
   cd frontend/liff
   cp ../dashboard/.eslintrc.json .
   npm run lint
   ```

### 下週行動 (Sprint 4 Week 2)

4. **代碼格式化 & Ruff 修復**:
   ```bash
   uv run black src/
   uv run ruff check src/ --fix
   ```

5. **異常處理改善** (手動審查每個 `except` 區塊):
   ```python
   # 統一使用 raise ... from e
   except ValueError as e:
       raise HTTPException(...) from e
   ```

6. **Dashboard ESLint 修復**:
   ```bash
   cd frontend/dashboard
   npm run lint --fix
   # 手動修復 any 類型問題
   ```

### 長期改善 (Sprint 11)

7. **建立 CI/CD 品質門檻**:
   ```yaml
   # .github/workflows/quality-check.yml
   - name: Code Quality
     run: |
       uv run black src/ --check
       uv run ruff check src/
       uv run mypy src/
       uv run pytest --cov=backend --cov-fail-under=80
   ```

8. **建立 Pre-commit Hook**:
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       hooks:
         - id: black
     - repo: https://github.com/astral-sh/ruff-pre-commit
       hooks:
         - id: ruff
           args: [--fix]
   ```

---

## 📊 品質改善指標 (Quality Improvement Metrics)

### 目標設定

| 指標 | 當前 | Sprint 4 目標 | Sprint 11 目標 |
|-----|------|--------------|---------------|
| **Black 合規率** | 64% (107/168) | 100% | 100% |
| **Ruff 錯誤數** | 174 | <20 | 0 |
| **Mypy 通過率** | 0% (模組衝突) | 100% | 100% |
| **測試覆蓋率** | 0% (無法執行) | ≥60% | ≥80% |
| **前端 ESLint** | Dashboard 8 errors, LIFF 無配置 | 0 errors | 0 errors + 0 warnings |

### 成功標準

**Sprint 4 完成標準**:
- ✅ 所有 P0 問題修復
- ✅ 所有 P1 問題修復
- ✅ 測試覆蓋率 ≥ 60%
- ✅ CI/CD 品質檢查通過

**Sprint 11 完成標準**:
- ✅ 所有技術債清零
- ✅ 測試覆蓋率 ≥ 80%
- ✅ 0 Ruff 錯誤
- ✅ 0 ESLint 錯誤/警告

---

## 🔗 相關文檔

- **Code Review Guide**: `docs/11_code_review_and_refactoring_guide.md`
- **Security Checklist**: `docs/13_security_and_readiness_checklists.md`
- **Sprint 3 Final Summary**: `docs/testing/sprint3_final_summary.md`
- **Sprint 3 Code Review**: `docs/testing/sprint3_code_review_findings.md`

---

**報告建立**: 2025-10-23
**下次審查**: Sprint 4 Week 2 (2025-11-08) - 驗證 P0/P1 修復狀態
**審查人員**: Claude Code (TaskMaster Hub - Code Quality Specialist)
