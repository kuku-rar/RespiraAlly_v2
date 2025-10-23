# Changelog - 2025-10-22

## 📦 2025-10-23 更新: Sprint 3 Week 6 完成 - LIFF Survey + 表單修正 ✅

**版本**: v3.3.2
**日期**: 2025-10-23 14:30
**狀態**: Sprint 3 Week 6 完成，進度 91.7%

### 🎉 完成任務

**Task 5.3 - LIFF 問卷頁** (24h)
- ✅ CAT 8 題表單 UI (elder-friendly design)
- ✅ mMRC 1 題表單 + 結果顯示
- ✅ CAT → mMRC → Thank You 自動導向流程
- ✅ Thank You 頁面顯示雙問卷分數

**Task 5.6 - CAT 量表無障礙設計 (TTS)** (8h)
- ✅ Web Speech API 整合 (useTTS Hook)
- ✅ 問卷頁朗讀按鈕整合 (CAT + mMRC)
- ✅ 基本樣式與無障礙標籤

**用戶反饋修正** (額外工作)
1. ✅ 註冊頁面欄位更新：
   - 移除：COPD 分期、確診日期
   - 新增：醫院病歷號、身高、體重、菸齡
   - 驗證範圍：身高 100-250cm, 體重 30-200kg, 菸齡 0-80年
2. ✅ 性別按鈕 UX 改善：
   - 添加選中狀態視覺指示器
   - 綠色邊框、背景、陰影效果
   - 選中時顯示 ✓ 標記
3. ✅ 每日日誌符合 ADR-009：
   - 移除：日期選擇器 (自動設為今日)、steps_count
   - 新增：exercise_minutes (0-480), smoking_count (0-100)
4. ✅ Survey 流程自動化：
   - CAT 填寫完自動導向 mMRC (不顯示結果頁)
   - mMRC 完成後導向 Thank You 頁面
   - Thank You 頁面同時顯示 CAT 和 mMRC 分數

### 📊 更新進度

| 項目 | 數值 | 變化 |
|------|------|------|
| **Sprint 3 已完成** | 88h | +32h |
| **Sprint 3 進度** | 91.7% | +33.4% |
| **Sprint 3 剩餘** | 8h | -32h |
| **專案總完成** | 443.75h | +32h |
| **專案總進度** | ~43.0% | +3.1% |

### 🔗 詳細文檔

- **Git Commits**:
  - `a1dea9e` - fix(liff): update registration and daily log forms per user feedback
  - `8dbfb5c` - feat(liff): implement CAT → mMRC → Thank You survey flow
- **相關 ADR**:
  - ADR-009: Daily Log Schema Redesign
  - ADR-010: Sprint 3 MVP Scope Reduction
  - ADR-011: CAT Accessibility TTS Solution

### 🎯 技術亮點

**1. 表單驗證增強** (Register.tsx, LogForm.tsx)
- TypeScript 型別更新：PatientRegisterRequest, DailyLogBase
- 數值範圍驗證：身高、體重、菸齡、運動、吸菸
- React Hook Form 整合：watch() 追蹤選擇狀態

**2. UX 設計改善** (Register.tsx)
- 性別按鈕條件樣式：`selectedGender === value ? 'border-green-600 bg-green-50 shadow-md' : 'border-gray-300'`
- 選中指示器：✓ 標記 + 高對比配色
- 保持 hover 效果：未選中按鈕 hover 時預覽選中樣式

**3. Survey 流程狀態管理** (SurveyPage.tsx)
- 新增 `CompletedSurveys` 介面儲存雙問卷結果
- 條件導向邏輯：CAT → mMRC (setView('form')), mMRC → Thank You (setView('thankyou'))
- TTS 整合：每個步驟自動朗讀問題文字

**4. Thank You 頁面設計** (SurveyPage.tsx lines 403-500)
- 雙卡片顯示：CAT 分數卡 (藍色) + mMRC 等級卡 (綠色)
- 高對比配色：易讀性優化，符合長者友善設計
- 兩個行動按鈕：返回首頁 (主要)、重新填寫 (次要)

### 📝 檔案變更摘要

**類型定義更新**:
- `frontend/liff/src/types/auth.ts` - 移除 COPDStage, 更新 PatientRegisterRequest
- `frontend/liff/src/types/daily-log.ts` - 更新 DailyLogBase, DailyLogFormData

**API & Mock 更新**:
- `frontend/liff/src/api/auth.ts` - 更新 mock 驗證邏輯
- `frontend/liff/src/api/daily-log.ts` - 更新 mock 資料和驗證

**UI 組件更新**:
- `frontend/liff/src/pages/Register.tsx` - 表單欄位替換 + 性別按鈕 UX
- `frontend/liff/src/pages/LogForm.tsx` - 移除日期選擇 + 更新欄位
- `frontend/liff/src/pages/SurveyPage.tsx` - 流程自動化 + Thank You 頁面

---

## 📦 2025-10-23 更新: Task 5.1 完成 ✅

**版本**: v3.3.1
**日期**: 2025-10-23 03:30
**狀態**: Sprint 3 Week 5 完成，進度 58.3%

### 🎉 完成任務

**Task 5.1 - 個案 360° Dashboard 頁面** (32h)
- ✅ Task 5.1.1: TanStack Query 基礎架構 + API Hooks (16h)
- ✅ Task 5.1.2: PatientHeader + PatientTabs 組件 (8h)
- ⏭️ Task 5.1.3: DailyLogsTrendChart (跳過 - P2)
- ✅ Task 5.1.4: 錯誤處理 + Loading 狀態 (8h)

### 📊 更新進度

| 項目 | 數值 | 變化 |
|------|------|------|
| **Sprint 3 已完成** | 56h | +32h |
| **Sprint 3 進度** | 58.3% | +33.3% |
| **Sprint 3 剩餘** | 40h | -32h |

### 🔗 詳細文檔

- **CHANGELOG v4.11**: 完整技術實現細節
- **Sprint 3 Development Plan**: Week 5 進度表格已更新
- **Git Commits**:
  - `511cf44` - Task 5.1.1 (TanStack Query)
  - `2215ecb` - Task 5.1.2 (Header + Tabs)
  - `f2a9e68` - Task 5.1.4 (Error Handling)

---

## Sprint 3 MVP 範圍調整 - 實用主義路線

**版本**: v3.3.0
**日期**: 2025-10-22 21:55
**狀態**: Sprint 3 規劃重大調整

---

## 🎯 重大決策：採用實用主義路線

### 📋 決策摘要

基於 **Linus Torvalds 實用主義哲學**，對 Sprint 3 進行範圍調整：
- ✅ **保留核心**: 360° 頁面、LIFF 問卷、Survey API
- ✅ **簡化 TTS**: 24h → 8h (Web Speech API 實現)
- ⏸ **延後營養評估**: 56h → Sprint 6+ (MVP 後)
- 📊 **總工時**: 176h → 96h (減少 80h)

---

## 📊 Sprint 3 調整細節

### ✅ 保留任務 (Core MVP)

| 任務 | 工時 | 狀態 | 優先級 | 理由 |
|------|------|------|--------|------|
| **5.1 個案 360° 頁面** | 32h | ✅ | P0 | 治療師核心工作流 (已完成 - 2025-10-23) |
| **5.2 CAT/mMRC 問卷 API** | 24h | ✅ | P0 | 已完成 (Domain Events + 20+ 測試) |
| **5.3 LIFF 問卷頁** | 24h | ⬜ | P0 | 病患填答核心功能 |
| **5.4 趨勢圖表元件** | 16h | ⏭️ | P2 | 延後至 Sprint 4+ |
| **5.6 CAT TTS 無障礙** | 8h | ⬜ | P1 | 簡化後可接受 |
| **小計** | **104h** | **58.3%** | - | **聚焦 MVP** |

### ⏸ 延後任務 (Post-MVP)

| 任務 | 工時 | 延後至 | 理由 |
|------|------|--------|------|
| **5.5 營養評估 KPI** | 56h | Sprint 6+ | 需求不明確 (量表未選定、風險權重未確認) |
| - 營養測量 API | 16h | - | - |
| - 營養量表 API | 12h | - | - |
| - Dashboard 輸入介面 | 12h | - | - |
| - 風險計算整合 | 8h | - | - |
| - LIFF 趨勢顯示 | 8h | - | - |

---

## 🔧 TTS 功能大幅簡化

### 原計劃 vs 新方案

| 項目 | 原計劃 | 新方案 | 節省 |
|------|--------|--------|------|
| **技術方案** | OpenAI TTS / Azure Speech | Web Speech API | 零後端成本 |
| **TTS 整合** | 12h (後端 API + 音檔管理) | 2h (useTTS Hook) | -10h |
| **控制介面** | 8h (播放控制 + 設定頁) | 2h (基本按鈕) | -6h |
| **測試** | 4h (多瀏覽器 + 音質驗證) | 2h (iOS/Android 基本測試) | -2h |
| **總計** | **24h** | **8h** | **-16h** |

### 新方案技術細節

```typescript
// useTTS Hook - 超簡單實現
import { useState } from 'react';

export const useTTS = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);

  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-TW';
      utterance.rate = 0.9; // 老年人友善語速

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    }
  };

  const stop = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  return { speak, stop, isSpeaking };
};
```

**功能範圍**:
- ✅ 基本朗讀 (播放/暫停/停止)
- ✅ 繁體中文語音 (系統預設)
- ✅ 語速調整 (0.9x)
- ❌ 語音選擇 (不支援)
- ❌ 音檔存儲 (不需要)

**瀏覽器支援**:
- iOS Safari 14+ (LINE 內建瀏覽器) ✅
- Android Chrome 90+ ✅
- Desktop Chrome/Edge (開發測試) ✅

---

## 🚫 營養評估延後原因

### Linus 式三個問題

1. **這是真問題還是臆想的？**
   - ⚠️ 客戶未明確說要用哪個量表 (MNA-SF vs MUST)
   - ⚠️ 風險權重未確認
   - ⚠️ InBody 其他指標未確認

2. **有更簡單的方法嗎？**
   - ✅ 先完成核心功能 (360° + 問卷)
   - ✅ 等客戶明確需求後再做

3. **會破壞什麼嗎？**
   - ✅ 不會破壞現有架構 (獨立功能模組)
   - ✅ 延後不影響 MVP 交付

### 待客戶確認事項

在 Sprint 3 結束前，需客戶明確回答：
- [ ] 營養量表選擇: MNA-SF vs MUST vs 其他？
- [ ] InBody 必須收集的指標有哪些？
- [ ] 營養風險權重: 在總風險評分中占多少比例？
- [ ] 測量頻率: 治療師能確保 1-3 月執行一次嗎？
- [ ] 業務必要性: 為什麼現在就要做？能否延後到 Sprint 5-6？

**如果確認必要**: 排入 Sprint 6 (MVP 後優化期)
**如果不急**: 延後到 Sprint 7+ 或根據用戶反饋決定

---

## 📈 專案進度更新

### 整體進度

| 項目 | 原計劃 | 調整後 | 最新 (2025-10-23) |
|------|--------|--------|-------------------|
| **Sprint 3 總工時** | 176h | 96h | 96h |
| **Sprint 3 已完成** | 24h | 24h | **56h** ⬆️ |
| **Sprint 3 進度** | 13.6% | 25.0% | **58.3%** ⬆️ |
| **專案總工時** | 1113h | 1033h | 1033h |
| **專案已完成** | 387.95h | 411.95h | **443.95h** ⬆️ |
| **專案進度** | ~34.9% | ~39.9% | **~43.0%** ⬆️ |

### Sprint 6 調整

營養評估 (56h) 移入 Sprint 6:
- **原計劃**: Sprint 6: AI 語音處理鏈 [88h]
- **調整後**: Sprint 6: AI 語音 + 營養評估 [144h]

---

## 🎯 接下來的行動計畫

### Week 5 (本週剩餘) - 32h
```
🎯 Task 5.1 - 個案 360° 頁面
├─ Day 1-2: 靜態資料顯示 (Patient + DailyLog + Survey) [16h]
├─ Day 3: 錯誤處理與載入狀態 [8h]
└─ Day 4: 手動測試與問題修復 [8h]
```

### Week 6 (下週) - 32h
```
🎯 Task 5.3 - LIFF 問卷頁 [24h]
├─ Day 1-2: CAT 8 題表單 UI [12h]
├─ Day 3: mMRC 1 題 + 結果顯示 [8h]
└─ Day 4: 測試與修復 [4h]

🟢 Task 5.6 - CAT TTS [8h]
└─ Day 4: useTTS Hook + 朗讀按鈕 + 測試 [8h]

🟡 Task 5.4 - 趨勢圖表 (可選) [16h]
└─ Day 5-6: 如有時間才做
```

---

## 📝 Definition of Done (DoD)

### MUST (必須完成)
- ✅ Survey API 完成 (已完成)
- ⬜ 個案 360° 頁面顯示 Patient + DailyLog + Survey
- ⬜ LIFF 可填寫 CAT (8 題) 和 mMRC (1 題)
- ⬜ 問卷分數正確計算並顯示
- ⬜ 基本 TTS 朗讀功能 (CAT + mMRC)
- ⬜ 基本錯誤處理 (網路失敗、API 錯誤)
- ⬜ 手動測試通過 (治療師 + 病患角色)

### SHOULD (最好完成)
- ⬜ 趨勢圖表元件 (日誌 or 問卷趨勢)

### DEFERRED (明確延後)
- ~~營養評估 KPI~~ → MVP 後 (Sprint 6+)
- ~~AI Worker 語音~~ → MVP 後 (Sprint 6)

---

## 🎨 ADR 記錄

**ADR-XXX**: Sprint 3 MVP 範圍縮減決策

**決策**: 延後營養評估 (56h) 至 MVP 後，簡化 TTS (24h→8h)

**理由**:
1. **實用主義**: 聚焦 MVP 核心功能，避免過度設計
2. **需求不明**: 營養量表、風險權重、InBody 指標未確認
3. **技術簡化**: Web Speech API 足夠滿足基礎無障礙需求
4. **交付穩定**: 減少 80h 工時，提升 Sprint 3 準時交付率

**影響**:
- ✅ Sprint 3 工時更合理 (96h vs 176h)
- ✅ 聚焦治療師和病患核心工作流
- ⏸ 營養評估需等客戶確認後才實作
- ⏸ MVP 不含營養風險評分

**替代方案**:
- ❌ 硬做營養評估 → 工時爆表，延遲交付，客戶可能不需要
- ❌ 完全移除 TTS → 失去無障礙加分項

**批准**: Technical Lead, Product Manager
**日期**: 2025-10-22

---

## 💬 Linus 式總結

> **"Theory and practice sometimes clash. Theory loses. Every single time."**
> （理論與實踐有時會衝突。每次輸的都是理論。）

**我們做對了三件事**:
1. **識別真問題** - MVP 不需要營養評估，那就不做
2. **避免過度設計** - Web Speech API 夠用就別搞複雜的
3. **聚焦交付** - 讓治療師能看病患資料，病患能填問卷，就是勝利

**接下來就是執行。Talk is cheap. Show me the code.** 🚀

---

**變更記錄**:
- [2025-10-22 21:55] 創建 Changelog - Sprint 3 MVP 範圍調整
- [2025-10-22 21:55] 更新 WBS v3.3.0 - TTS 簡化、營養評估延後

**相關文件**:
- WBS: docs/16_wbs_development_plan.md (v3.3.0)
- 總 Changelog: CHANGELOG.md
- ADR: (待創建) ADR-XXX Sprint 3 MVP Scope Reduction

---

**維護者**: RespiraAlly Development Team / TaskMaster Hub
**審核者**: Technical Lead, Product Manager
