# Alert System E2E 測試計劃
**Sprint 4 - Alert System MVP Testing**
**Date**: 2025-10-27
**Tester**: Claude Code
**Status**: Ready for Execution

---

## 📋 測試目標

驗證 Alert System 的完整功能流程，從警示顯示到詳情查看的用戶體驗。

---

## 🎯 測試範圍

### 涵蓋功能
- ✅ Alert List 顯示與篩選
- ✅ Alert Detail Modal 開啟與關閉
- ✅ Alert Badge 顯示與互動
- ✅ PatientTabs 中的 Alerts 分頁
- ✅ AlertBadge 自動切換分頁
- ✅ 完整的點擊流程

### 不涵蓋功能（Sprint 5）
- ❌ 警示確認功能（Acknowledge）
- ❌ 警示解決功能（Resolve）
- ❌ 真實 API 資料整合

---

## 🔧 測試環境設定

### 前提條件
1. Frontend Dashboard 服務運行於 `http://localhost:3000`
2. 環境變數設定為 Mock 模式：
   ```bash
   NEXT_PUBLIC_MOCK_MODE=true
   ```
3. PostgreSQL 資料庫運行（Port 15432）
4. Playwright MCP 已安裝並可用

### 測試資料（Mock 模式）
使用前端內建的 Mock 資料：
- **Mock 病患 ID 1**: `00000000-0000-0000-0000-000000000001` (有 2 個警示)
- **Mock 病患 ID 2**: `00000000-0000-0000-0000-000000000002` (有 1 個警示)
- **Mock 病患 ID 999**: `00000000-0000-0000-0000-000000000999` (無警示)

---

## 📝 測試案例

### Test Suite 1: Alert Test Page（警示測試頁面）

#### TC-1.1: 訪問測試頁面
**URL**: `http://localhost:3000/alerts/test`

**步驟**:
1. 導航到 `/alerts/test`
2. 等待頁面載入完成

**預期結果**:
- ✅ 頁面標題顯示「警示系統測試頁面」
- ✅ 顯示 Sprint 4 MVP 標籤
- ✅ 顯示病患選擇器（4 個測試病患）
- ✅ 顯示 10 項測試檢查清單
- ✅ 顯示整合說明區塊

---

#### TC-1.2: AlertList 基本顯示
**前置條件**: 測試頁面已載入，選擇病患 1

**步驟**:
1. 確認病患 1 被選中
2. 觀察 AlertList 顯示

**預期結果**:
- ✅ 顯示篩選器（嚴重程度、狀態、警示類型）
- ✅ 顯示警示列表表格
- ✅ 顯示至少 1 個警示（Mock 資料）
- ✅ 每個警示行顯示：類型、嚴重程度、狀態、觸發時間、臨床指標
- ✅ 顏色編碼正確（紅色=CRITICAL/HIGH，黃色=MEDIUM，藍色=LOW）

---

#### TC-1.3: AlertList 篩選功能
**前置條件**: AlertList 已顯示

**步驟**:
1. 點擊「嚴重程度」下拉選單 → 選擇「嚴重」
2. 觀察列表變化
3. 點擊「狀態」下拉選單 → 選擇「活動中」
4. 觀察列表變化
5. 點擊「警示類型」下拉選單 → 選擇「GOLD Group E」
6. 觀察列表變化
7. 重設所有篩選器（選擇「全部」）

**預期結果**:
- ✅ 篩選器變更時列表即時更新
- ✅ 只顯示符合篩選條件的警示
- ✅ 重設篩選器後顯示所有警示
- ✅ 頁碼重設為第 1 頁

---

#### TC-1.4: 開啟 AlertDetailModal
**前置條件**: AlertList 顯示至少 1 個警示

**步驟**:
1. 點擊第一個警示行
2. 等待 Modal 開啟

**預期結果**:
- ✅ AlertDetailModal 開啟
- ✅ 顯示黑色半透明背景（backdrop）
- ✅ Modal 置中顯示
- ✅ 顯示關閉按鈕（右上角 ×）
- ✅ 顯示警示詳情：
  - 警示類型
  - 嚴重程度（帶顏色標籤）
  - 狀態（帶顏色標籤）
  - 警示 ID
- ✅ 顯示時間軸區段：
  - 觸發時間
  - 確認時間（如有）
  - 解決時間（如有）
  - 建立時間
  - 更新時間
- ✅ 顯示臨床指標卡片（如有）：
  - CAT 分數
  - mMRC 分級
  - GOLD 分級
  - 惡化次數
  - 住院次數
- ✅ 顯示 Metadata JSON 檢視器

---

#### TC-1.5: 關閉 AlertDetailModal
**前置條件**: AlertDetailModal 已開啟

**測試案例 A - 點擊關閉按鈕**:
1. 點擊右上角關閉按鈕（×）

**測試案例 B - 點擊背景**:
1. 點擊 Modal 外的黑色背景區域

**測試案例 C - 點擊底部關閉按鈕**:
1. 點擊底部的「關閉」按鈕

**預期結果**（所有案例）:
- ✅ Modal 關閉
- ✅ 回到 AlertList 頁面
- ✅ AlertList 仍顯示原有的篩選與分頁狀態

---

#### TC-1.6: 分頁功能
**前置條件**: AlertList 顯示超過 20 個警示（需要多頁）

**步驟**:
1. 觀察分頁控制顯示
2. 點擊「下一頁」按鈕
3. 觀察頁碼變化
4. 點擊「上一頁」按鈕
5. 觀察頁碼變化

**預期結果**:
- ✅ 顯示「第 X / Y 頁」
- ✅ 顯示「顯示第 X - Y 筆，共 Z 筆警示」
- ✅ 上一頁/下一頁按鈕狀態正確（禁用/啟用）
- ✅ 點擊後頁碼正確更新
- ✅ 列表內容更新為新頁資料

---

#### TC-1.7: 空狀態測試
**前置條件**: 選擇無警示的病患（病患 999）

**步驟**:
1. 點擊「病患 999 (無警示)」按鈕
2. 觀察 AlertList 顯示

**預期結果**:
- ✅ 顯示空狀態圖示（🔔）
- ✅ 顯示「目前沒有警示」訊息
- ✅ 顯示輔助說明文字
- ✅ 無表格資料行顯示

---

### Test Suite 2: Patient Detail Page Integration（病患詳情頁整合）

#### TC-2.1: AlertBadge 顯示
**URL**: `http://localhost:3000/patients/[patient_id]`
**病患 ID**: 使用有警示的 Mock 病患

**步驟**:
1. 導航到病患詳情頁面
2. 等待頁面載入
3. 觀察 PatientHeader 區域

**預期結果**:
- ✅ PatientHeader 顯示病患基本資訊
- ✅ 顯示 AlertBadge（紅色徽章）
- ✅ AlertBadge 顯示正確的活動警示數量
- ✅ AlertBadge 有鈴鐺圖示 (🔔)
- ✅ AlertBadge 有脈衝動畫效果
- ✅ AlertBadge 有 hover 效果

**若無警示的病患**:
- ✅ AlertBadge 不顯示

---

#### TC-2.2: PatientTabs 警示分頁顯示
**前置條件**: 病患詳情頁面已載入

**步驟**:
1. 觀察 PatientTabs 區域
2. 檢查分頁標籤

**預期結果**:
- ✅ 顯示 4 個分頁：基本資料、每日紀錄、問卷評估、警示通知
- ✅ 警示通知分頁有鈴鐺圖示 (🔔)
- ✅ 預設停留在「基本資料」分頁

---

#### TC-2.3: 手動切換到警示分頁
**前置條件**: 病患詳情頁面已載入

**步驟**:
1. 點擊「警示通知」分頁標籤
2. 等待內容載入

**預期結果**:
- ✅ 分頁標籤變為藍色（active 狀態）
- ✅ 底部藍色指示條顯示
- ✅ 分頁內容區顯示：
  - 「病患警示通知」標題
  - 說明文字：「根據臨床指標自動產生的風險警示與提醒」
  - AlertList 元件（含篩選器）
- ✅ 顯示該病患的所有警示

---

#### TC-2.4: AlertBadge 自動切換分頁
**前置條件**: 病患詳情頁面已載入，停留在「基本資料」分頁

**步驟**:
1. 確認當前在「基本資料」分頁
2. 點擊 PatientHeader 中的 AlertBadge
3. 觀察頁面變化

**預期結果**:
- ✅ 自動切換到「警示通知」分頁
- ✅ URL hash 變為 `#alerts`
- ✅ 平滑滾動至警示區段
- ✅ AlertList 顯示該病患的警示
- ✅ 瀏覽器回上一頁功能正常（回到基本資料分頁）

---

#### TC-2.5: 警示分頁中的完整流程
**前置條件**: 已切換到警示分頁

**步驟**:
1. 觀察 AlertList 顯示
2. 使用篩選器篩選警示
3. 點擊一個警示行
4. 檢查 AlertDetailModal 顯示
5. 查看時間軸、臨床指標、Metadata
6. 關閉 Modal
7. 切換到其他分頁（如「基本資料」）
8. 再次切換回「警示通知」

**預期結果**:
- ✅ AlertList 功能正常（同 TC-1.2 ~ TC-1.6）
- ✅ AlertDetailModal 顯示完整（同 TC-1.4）
- ✅ 關閉 Modal 後回到 AlertList
- ✅ 分頁切換流暢
- ✅ 警示分頁狀態保持（篩選條件保留）

---

#### TC-2.6: 直接 URL 訪問警示分頁
**URL**: `http://localhost:3000/patients/[patient_id]#alerts`

**步驟**:
1. 直接在瀏覽器輸入完整 URL（含 `#alerts`）
2. 按 Enter
3. 等待頁面載入

**預期結果**:
- ✅ 頁面載入完成
- ✅ 自動顯示「警示通知」分頁（不是基本資料）
- ✅ AlertList 正常顯示
- ✅ 可以正常操作所有功能

---

### Test Suite 3: 跨瀏覽器與響應式測試

#### TC-3.1: 桌面端顯示（1920x1080）
**環境**: Desktop, 1920x1080

**測試項目**:
- ✅ AlertList 表格完整顯示（5 個欄位）
- ✅ AlertDetailModal 寬度適中（max-w-4xl）
- ✅ PatientTabs 分頁橫向排列
- ✅ AlertBadge 大小適中
- ✅ 所有文字清晰可讀

#### TC-3.2: 筆電端顯示（1366x768）
**環境**: Laptop, 1366x768

**測試項目**:
- ✅ AlertList 表格可滾動
- ✅ AlertDetailModal 不超出螢幕
- ✅ 臨床指標卡片適當排列
- ✅ 篩選器元件適當換行

#### TC-3.3: 平板端顯示（768x1024）
**環境**: Tablet, 768x1024 (Portrait)

**測試項目**:
- ✅ AlertList 表格可橫向滾動
- ✅ PatientTabs 分頁縮小但可點擊
- ✅ AlertDetailModal 佔據大部分螢幕
- ✅ 臨床指標卡片垂直排列

---

### Test Suite 4: 長者友善設計驗證

#### TC-4.1: 字體大小檢查
**檢查項目**:
- ✅ 標題使用 text-2xl 或更大（≥24px）
- ✅ 正文使用 text-lg 或 text-base（≥16px）
- ✅ 小字使用 text-sm（≥14px）
- ✅ 避免使用 text-xs（<12px）

#### TC-4.2: 顏色對比檢查
**檢查項目**:
- ✅ 嚴重程度標籤顏色清晰（紅/橙/黃/藍）
- ✅ 狀態標籤顏色清晰（紅/橙/綠）
- ✅ 文字與背景對比度 ≥ 4.5:1
- ✅ 連結與按鈕顏色明顯

#### TC-4.3: 可點擊區域檢查
**檢查項目**:
- ✅ AlertBadge 按鈕 ≥ 44px 高度
- ✅ 警示行可點擊區域足夠大
- ✅ Modal 關閉按鈕 ≥ 44px
- ✅ 分頁標籤 ≥ 44px 高度
- ✅ 篩選器下拉選單 ≥ 44px

---

## 🐛 已知問題與限制

1. **Mock 模式警示類型**
   - Mock 資料使用新的警示類型（GOLD_GROUP_E, HIGH_CAT_SCORE, FREQUENT_EXACERBATIONS）
   - 資料庫中的警示是舊類型（HIGH_RISK_DETECTED）
   - **解決方案**: 先使用 Mock 模式測試，後續整合真實 API

2. **警示確認/解決功能**
   - 目前顯示 "此功能將於 Sprint 5 實作" 提示
   - 按鈕點擊會彈出 alert 訊息
   - **狀態**: 按計劃，Sprint 5 實作

3. **分頁限制**
   - Mock 模式下固定顯示 4 個警示
   - 無法測試大量警示的分頁功能
   - **解決方案**: 整合真實 API 後測試

---

## ✅ 測試通過標準

### 必須通過（P0）
- [  ] TC-1.2: AlertList 基本顯示
- [  ] TC-1.4: 開啟 AlertDetailModal
- [  ] TC-1.5: 關閉 AlertDetailModal
- [  ] TC-2.1: AlertBadge 顯示
- [  ] TC-2.4: AlertBadge 自動切換分頁
- [  ] TC-2.5: 警示分頁中的完整流程

### 應該通過（P1）
- [  ] TC-1.3: AlertList 篩選功能
- [  ] TC-1.7: 空狀態測試
- [  ] TC-2.6: 直接 URL 訪問警示分頁
- [  ] TC-4: 長者友善設計驗證

### 可選通過（P2）
- [  ] TC-1.6: 分頁功能（需要更多測試資料）
- [  ] TC-3: 跨瀏覽器與響應式測試

---

## 📊 測試執行記錄

### 測試環境
- **Date**: ___________
- **Tester**: ___________
- **Browser**: ___________
- **Version**: ___________
- **OS**: ___________

### 測試結果
- **Total Test Cases**: 22
- **Passed**: ___
- **Failed**: ___
- **Blocked**: ___
- **Pass Rate**: ___%

### 重大缺陷
| ID | Severity | Description | Status |
|----|----------|-------------|--------|
|    |          |             |        |

---

## 📝 測試執行步驟（使用 Playwright）

### 前置作業
```bash
# 1. 啟動 Frontend Dashboard
cd frontend/dashboard
npm run dev

# 2. 確認服務運行
curl http://localhost:3000

# 3. 設定 Mock 模式（如果尚未設定）
# 編輯 .env.local
NEXT_PUBLIC_MOCK_MODE=true
```

### 執行測試
```bash
# 使用 Playwright MCP 執行測試
# 開啟測試頁面
mcp__playwright__browser_navigate(url="http://localhost:3000/alerts/test")

# 等待頁面載入
mcp__playwright__browser_wait_for(text="警示系統測試頁面")

# 截圖記錄
mcp__playwright__browser_take_screenshot(filename="alert-test-page.png")

# ... 繼續測試流程
```

---

## 🎯 下一步

1. **執行測試** - 使用 Playwright MCP 執行所有測試案例
2. **記錄結果** - 填寫測試執行記錄
3. **回報缺陷** - 建立 GitHub Issues
4. **準備 Sprint 5** - 規劃警示確認/解決功能

---

**測試計劃完成** ✅
**準備執行測試** 🚀
