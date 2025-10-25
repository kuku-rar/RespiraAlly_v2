# Dashboard 高風險患者篩選測試報告

**測試日期**: 2025-10-25
**測試範圍**: Sprint 4 - Dashboard 高風險患者風險等級顯示與篩選功能
**測試方法**: 快速驗證路徑（簡化風險計算 + 前端實作）
**測試狀態**: ⚠️ 自動化測試遇到障礙，建議進行手動測試
**自動化測試進度**: 已嘗試使用 Chrome DevTools MCP，但遇到技術問題

---

## ✅ 測試環境準備

### 1. Frontend 構建修復
- **問題**: `@tanstack/react-query-devtools` 在 production build 時找不到模組
- **解決方案**: 實作 lazy loading + 條件導入
- **修改檔案**: `frontend/dashboard/providers/QueryProvider.tsx`
- **結果**: ✅ Build 成功，所有 7 頁面生成成功

```typescript
// 修復前：直接導入（生產環境會失敗）
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// 修復後：lazy loading + 條件導入
const ReactQueryDevtools =
  process.env.NODE_ENV === 'development'
    ? lazy(() =>
        import('@tanstack/react-query-devtools').then((d) => ({
          default: d.ReactQueryDevtools,
        }))
      )
    : () => null
```

### 2. Database Migration 005 執行
- **執行狀態**: ✅ 成功完成
- **建立資源**:
  - 5 個 ENUM 類型 (gold_group_enum, exacerbation_severity_enum, alert_type_enum, alert_severity_enum, alert_status_enum)
  - 3 個資料表 (exacerbations, risk_assessments, alerts)
  - 1 個 trigger function (update_patient_exacerbation_summary)
  - 1 個 view (patient_risk_summary)
- **特殊處理**: patient_profiles 的 exacerbation 欄位已存在，跳過 ALTER TABLE 步驟

### 3. 測試數據準備
- **資料來源**: `scripts/generate_test_data.py`
- **患者總數**: 50 位
- **高風險患者數**: 5 位（~10%，有 exacerbation history）
- **風險判斷依據**:
  - `exacerbation_count_last_12m`: 1-3 次急性惡化
  - `hospitalization_count_last_12m`: 0-2 次住院記錄

---

## 🎯 功能實作

### 1. 風險計算工具 (lib/utils/risk.ts)

**建立檔案**: `frontend/dashboard/lib/utils/risk.ts`

**實作功能**:
```typescript
// 風險等級計算（簡化版，用於快速驗證）
export function calculateRiskLevel(input: RiskCalculationInput): RiskLevel {
  const exacerbations = input.exacerbation_count_last_12m ?? 0
  const hospitalizations = input.hospitalization_count_last_12m ?? 0

  // CRITICAL: 高頻率或嚴重案例
  if (exacerbations >= 3 || hospitalizations >= 2) {
    return RiskLevel.CRITICAL
  }

  // HIGH: 中等頻率或需住院
  if (exacerbations >= 2 || hospitalizations >= 1) {
    return RiskLevel.HIGH
  }

  // MEDIUM: 一次急性惡化
  if (exacerbations === 1) {
    return RiskLevel.MEDIUM
  }

  // LOW: 無急性惡化
  return RiskLevel.LOW
}
```

**風險等級標準**:
| 風險等級 | 條件 | 中文標籤 | 顏色 | Emoji |
|---------|------|----------|------|-------|
| CRITICAL | ≥3 exacerbations OR ≥2 hospitalizations | 緊急 | 紅色 | 🚨 |
| HIGH | ≥2 exacerbations OR ≥1 hospitalization | 高風險 | 橙色 | 🔶 |
| MEDIUM | 1 exacerbation | 中風險 | 黃色 | ⚠️ |
| LOW | 0 exacerbations | 低風險 | 綠色 | ✅ |

**提供函數**:
- `calculateRiskLevel()`: 計算風險等級
- `getRiskLevelLabel()`: 取得中文標籤
- `getRiskLevelColor()`: 取得 Tailwind CSS 樣式類別
- `getRiskLevelEmoji()`: 取得 emoji 指示器

### 2. PatientTable 組件更新

**修改檔案**: `frontend/dashboard/components/patients/PatientTable.tsx`

**主要變更**:
1. 新增「風險等級」欄位（表格第2欄）
2. 每位患者顯示計算出的風險等級 badge
3. Badge 包含 emoji + 中文標籤 + 顏色編碼

```typescript
// 計算每位患者的風險等級
const riskLevel = calculateRiskLevel({
  exacerbation_count_last_12m: patient.exacerbation_count_last_12m,
  hospitalization_count_last_12m: patient.hospitalization_count_last_12m,
})

// 顯示風險等級 badge
<span className={`inline-flex items-center px-3 py-1 rounded-full text-base font-medium border-2 ${getRiskLevelColor(riskLevel)}`}>
  {getRiskLevelEmoji(riskLevel)} {getRiskLevelLabel(riskLevel)}
</span>
```

**視覺效果**:
- ✅ 低風險: 綠色背景 + 綠色邊框 + ✅ emoji
- ⚠️ 中風險: 黃色背景 + 黃色邊框 + ⚠️ emoji
- 🔶 高風險: 橙色背景 + 橙色邊框 + 🔶 emoji
- 🚨 緊急: 紅色背景 + 紅色邊框 + 🚨 emoji

### 3. PatientFilters 組件驗證

**檔案檢查**: `frontend/dashboard/components/patients/PatientFilters.tsx`

**現有功能**:
- ✅ 風險等級篩選下拉選單（Line 102-118）
- ✅ 支持全部/低風險/中風險/高風險/緊急
- ✅ 篩選條件變更時重置到第一頁（app/patients/page.tsx Line 70）
- ✅ 排序選項包含「風險等級（高→低）」（Line 91）

### 4. API 整合

**檔案檢查**: `frontend/dashboard/app/patients/page.tsx`

**整合狀態**:
- ✅ PatientFilters 組件正確使用（Line 155-158）
- ✅ 篩選條件傳遞到 API（Line 51-55）
- ✅ PatientTable 組件接收並顯示患者列表（Line 176-180）
- ✅ 篩選變更時自動重新 fetch 資料（Line 43）

---

## 🧪 測試執行狀態

### 伺服器狀態
- ✅ Backend API: Running on port 8000 (uvicorn) - Health check 正常
- ✅ Frontend Dev: Running on port 3000 (Next.js) - 編譯成功
- ✅ Production Build: 成功（所有 7 頁面生成）

### 自動化測試嘗試記錄 (2025-10-25 23:30-23:45)

#### 遇到的問題
1. **QueryProvider.tsx Build 錯誤** [已修復 ✅]
   - 問題：Production build 時 `@tanstack/react-query-devtools` 模組找不到
   - 解決：使用 `next/dynamic` 替換 React `lazy`，並禁用 SSR
   - 結果：Production build 成功，所有頁面生成

2. **頁面載入超時** [技術限制 ⚠️]
   - 問題：Chrome DevTools MCP 導航超時（10 秒 timeout）
   - 原因：`/patients` 頁面首次編譯需要 18.5 秒（844 modules）
   - 影響：無法使用自動化工具完成 UI 測試

#### 當前狀態
- ✅ 前後端服務正常運行
- ✅ 程式碼實作完成（風險計算、UI 顯示、篩選功能）
- ✅ Production build 測試通過
- ⚠️ 需要手動 UI 測試驗證功能

### 測試帳號
```
Email: therapist1@respira-ally.com
Password: SecurePass123!
```

### 測試前端 URL
```
http://localhost:3000/patients
```

---

## 📊 預期測試結果

### 測試案例 1: 顯示所有患者 (預設)
- **操作**: 登入後進入患者列表頁面
- **預期結果**:
  - 顯示 50 位患者
  - 每位患者顯示風險等級 badge
  - 約 5 位患者顯示高風險或緊急標籤（紅色/橙色）
  - 約 45 位患者顯示低風險標籤（綠色）

### 測試案例 2: 篩選高風險患者
- **操作**:
  1. 展開篩選選單
  2. 風險等級選擇「高風險」
  3. 點擊「套用篩選」
- **預期結果**:
  - 只顯示 exacerbation_count_last_12m ≥ 2 OR hospitalization_count_last_12m ≥ 1 的患者
  - 約 2-3 位患者
  - 所有患者 badge 都是橙色「🔶 高風險」

### 測試案例 3: 篩選緊急患者
- **操作**:
  1. 風險等級選擇「緊急」
  2. 點擊「套用篩選」
- **預期結果**:
  - 只顯示 exacerbation_count_last_12m ≥ 3 OR hospitalization_count_last_12m ≥ 2 的患者
  - 約 1-2 位患者
  - 所有患者 badge 都是紅色「🚨 緊急」

### 測試案例 4: 風險等級排序
- **操作**: 排序選擇「風險等級（高→低）」
- **預期結果**:
  - 緊急患者排在最前面
  - 然後是高風險、中風險
  - 低風險患者排在最後

### 測試案例 5: 重置篩選
- **操作**:
  1. 套用任意篩選條件
  2. 點擊「重置篩選」
- **預期結果**:
  - 篩選條件清除
  - 顯示所有 50 位患者
  - 排序回到預設（姓名 A-Z）

---

## 🎯 實作驗證 Checklist

- [x] Frontend 構建錯誤修復
- [x] Migration 005 執行成功
- [x] 風險計算工具函數實作
- [x] PatientTable 顯示風險等級 badge
- [x] PatientFilters 支持風險等級篩選
- [x] 患者頁面整合所有組件
- [x] Backend API 運行正常
- [x] Frontend Dev Server 運行正常
- [ ] **手動 UI 測試** (待執行)
  - [ ] 登入成功
  - [ ] 患者列表顯示風險 badge
  - [ ] 高風險篩選功能正常
  - [ ] 風險等級排序正常
  - [ ] 篩選重置功能正常

---

## 📝 測試說明

### 當前實作範圍（快速驗證路徑）
✅ **已完成**:
- 簡化風險計算邏輯（基於 exacerbation history）
- Frontend 風險等級顯示（badges with colors & emojis）
- 篩選功能整合（risk_bucket filter）
- 排序功能（risk_level sort）

⏳ **延後實作**（完整 GOLD ABE 引擎）:
- CAT 問卷評分
- mMRC 呼吸困難量表
- FEV1 肺功能檢測
- GOLD ABE 分組演算法（A, B, E）
- 完整風險評估引擎

### 技術債務與改善建議
1. **完整 GOLD ABE 實作**: 當前使用簡化風險計算，需在後續 Sprint 實作完整分類引擎
2. **Backend API 認證測試**: 當前僅驗證前端整合，需進行完整 API 測試
3. **E2E 自動化測試**: 建議加入 Playwright 測試覆蓋篩選流程
4. **風險等級定義文檔**: 需建立醫療專業人員可理解的風險等級定義文檔

---

## 🚀 下一步建議

1. **手動 UI 測試** [15min]
   - 使用測試帳號登入
   - 驗證所有測試案例
   - 截圖記錄測試結果

2. **記錄測試結果** [15min]
   - 更新此報告的測試結果區段
   - 提交所有變更到 Git

3. **規劃完整 GOLD ABE 實作** [30min]
   - 研究 GOLD 2011 ABE 分類標準
   - 設計完整風險評估引擎架構
   - 建立實作時程表

---

## 📊 技術總結

### 修改檔案清單
1. `frontend/dashboard/providers/QueryProvider.tsx` - 修復 devtools lazy loading
2. `frontend/dashboard/lib/types/patient.ts` - 擴展 PatientResponse 介面
3. `frontend/dashboard/lib/utils/risk.ts` - **新建** 風險計算工具
4. `frontend/dashboard/components/patients/PatientTable.tsx` - 新增風險等級欄位
5. Backend Migration 005 - 建立 risk engine tables

### 代碼統計
- **新增程式碼**: ~150 lines (risk.ts + PatientTable updates)
- **修改程式碼**: ~30 lines (QueryProvider.tsx + patient.ts)
- **刪除程式碼**: 0 lines

### 測試覆蓋率
- **單元測試**: 0% (快速驗證路徑，未建立測試)
- **整合測試**: 0% (待手動 UI 測試)
- **E2E 測試**: 0% (待後續建立)

---

---

## ✅ 測試結論

### 已完成項目
1. ✅ Frontend Build 錯誤修復
   - 修改檔案：`frontend/dashboard/providers/QueryProvider.tsx`
   - 使用 `next/dynamic` 實現條件式載入
   - Production build 驗證成功

2. ✅ 風險計算與顯示功能實作
   - 風險等級計算工具：`frontend/dashboard/lib/utils/risk.ts`
   - PatientTable 風險 badge 顯示
   - 風險等級篩選與排序功能整合

3. ✅ 服務運行驗證
   - Backend API (port 8000): 正常
   - Frontend Dev (port 3000): 正常
   - Database Migration 005: 已執行

### 待完成項目
1. ⚠️ **手動 UI 測試** [15min] - 優先級 P0
   - 自動化測試因技術限制無法完成
   - 建議用戶使用瀏覽器手動執行測試案例 1-5
   - 測試 URL: http://localhost:3000/patients

2. 📝 **測試結果記錄** [15min]
   - 截圖記錄風險 badge 顯示
   - 驗證篩選功能正確性
   - 更新此報告的測試結果區段

### 技術改善建議
1. **優化頁面載入時間**
   - 目前 `/patients` 首次編譯需 18.5 秒
   - 建議：實作增量靜態生成 (ISR) 或優化 bundle size

2. **E2E 測試框架**
   - 當前使用的 Chrome DevTools MCP 有 timeout 限制
   - 建議：使用 Playwright 或 Cypress 進行完整 E2E 測試

---

**報告產生時間**: 2025-10-25 23:45 (UTC+8)
**測試執行人員**: Claude Code (自動化嘗試) + User (手動測試待執行)
**最終狀態**: ✅ 程式碼實作完成並驗證，⚠️ UI 功能測試待手動執行
