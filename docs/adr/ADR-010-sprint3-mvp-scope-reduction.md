# ADR-010: Sprint 3 MVP 範圍縮減決策

**狀態**: ✅ 已批准 (Accepted)
**日期**: 2025-10-22
**決策者**: Technical Lead, Product Manager, TaskMaster Hub
**影響範圍**: Sprint 3 規劃、Sprint 6 調整、MVP 交付範圍

---

## 📋 背景 (Context)

### 問題描述

Sprint 3 原計劃包含以下功能：
- 個案 360° 頁面 (32h)
- CAT/mMRC 問卷系統 (24h) ✅ 已完成
- LIFF 問卷頁 (24h)
- 趨勢圖表元件 (16h)
- **營養評估 KPI (56h)** - 新增需求
- **CAT TTS 無障礙 (24h)** - 新增需求

**總工時**: 176h (+80h from v3.0)

### 發現的問題

1. **營養評估需求不明確**:
   - 量表選擇未確定 (MNA-SF vs MUST)
   - 風險權重未確認
   - InBody 其他指標未明確

2. **TTS 工時過高估算**:
   - 原估算 24h 假設需要後端 TTS API (OpenAI/Azure)
   - 實際 Web Speech API 即可滿足需求
   - 高估了 3 倍工時 (24h → 8h)

3. **MVP 交付風險**:
   - 176h 工時過重，可能延遲交付
   - 核心功能 (360° + 問卷) 被非核心功能稀釋注意力
   - 需求不明確的功能增加技術債風險

---

## 🎯 決策 (Decision)

### 採用實用主義路線 (Pragmatic Approach)

基於 **Linus Torvalds 實用主義哲學** ("Theory and practice sometimes clash. Theory loses.")，做出以下調整：

#### 1. 延後營養評估 (56h → Sprint 6+)

**理由**:
- ❌ 需求不明確 (量表、權重、指標未確認)
- ❌ 非 MVP 核心功能 (營養資料是低頻，1-3 月一次)
- ❌ 56h 工時過高，影響 Sprint 3 交付穩定性
- ✅ 延後不破壞架構 (獨立功能模組)
- ✅ 等客戶明確需求後再實作，避免返工

**待客戶確認**:
- 營養量表選擇: MNA-SF vs MUST？
- InBody 必須指標有哪些？
- 營養風險權重占比？
- 測量頻率與執行可行性？

#### 2. 簡化 TTS 實作 (24h → 8h)

**理由**:
- ✅ Web Speech API 足夠滿足基礎無障礙需求
- ✅ 零後端成本，零額外服務依賴
- ✅ 瀏覽器原生支援 (iOS Safari, Android Chrome)
- ❌ 不需要音檔存儲與管理
- ❌ 不需要複雜的播放控制介面

**功能範圍調整**:
- ✅ 保留: 基本朗讀 (播放/暫停/停止)
- ✅ 保留: 繁體中文語音、語速調整
- ❌ 移除: 語音選擇 (使用系統預設)
- ❌ 移除: 音檔存儲 (即時合成)

#### 3. 聚焦核心 MVP 功能

**保留 (P0-P1)**:
- 5.1 個案 360° 頁面 [32h] - P0 (治療師核心工作流)
- 5.2 Survey API [24h] - ✅ 已完成
- 5.3 LIFF 問卷頁 [24h] - P0 (病患填答核心)
- 5.6 CAT TTS [8h] - P1 (無障礙加分項)

**可選 (P2)**:
- 5.4 趨勢圖表 [16h] - P2 (錦上添花)

**延後 (Post-MVP)**:
- 5.5 營養評估 [56h] - Sprint 6+

---

## 🔧 技術方案 (Technical Approach)

### Web Speech API TTS 實作

**參考實現** (來自 `docs/frontend/cat_form.html`):

```javascript
function speak(text) {
  if (!('speechSynthesis' in window)) return;

  const synth = window.speechSynthesis;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'zh-TW'; // 台灣中文

  // 取消任何正在進行的語音
  synth.cancel();

  // 獲取中文語音
  const voices = synth.getVoices();
  const chineseVoice = voices.find(voice =>
    voice.lang.includes('zh-TW') || voice.lang.includes('cmn')
  );

  if (chineseVoice) {
    utter.voice = chineseVoice;
  }

  synth.speak(utter);
}
```

**React Hook 實作**:

```typescript
// hooks/useTTS.ts
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

### 無障礙設計原則 (參考 cat_form.html)

**已驗證的設計模式**:

1. **視覺無障礙**:
   - 高對比模式切換 (黑底黃字)
   - 大字體 (20-28px)
   - 清晰的視覺層級

2. **聽覺無障礙**:
   - 自動朗讀問題 (進入頁面時)
   - 語速調整 (0.9x, 老年人友善)
   - 繁體中文語音

3. **觸控無障礙**:
   - 大按鈕 (padding: 20px)
   - 清晰的按壓反饋 (hover/active 狀態)
   - 表情符號視覺提示 (✅😊😐🙁🤢🥵)

4. **認知無障礙**:
   - 白話文描述 (避免醫學術語)
   - 一次只顯示一個問題
   - 進度提示清晰

5. **ARIA 標籤**:
   ```html
   <button aria-label="分數0：完全沒咳嗽">
   <main role="main">
   <ul role="list">
   ```

---

## 📊 影響分析 (Consequences)

### ✅ 正面影響

1. **交付穩定性提升**:
   - Sprint 3 工時: 176h → 96h (減少 45%)
   - 更合理的工作量，降低延遲風險

2. **聚焦核心功能**:
   - 治療師 360° 視圖 (核心工作流)
   - 病患 LIFF 問卷 (核心交付)
   - 基礎無障礙 (加分項，成本低)

3. **技術簡化**:
   - Web Speech API 零額外依賴
   - 無需後端 TTS 服務
   - 無需音檔存儲與管理

4. **避免技術債**:
   - 延後需求不明確的功能
   - 避免返工與重構

5. **專案進度提升**:
   - 總工時: 1113h → 1033h (減少 7%)
   - 專案進度: 34.9% → 39.9% (+5.0%)

### ⚠️ 需注意的影響

1. **營養評估延後**:
   - MVP 不含營養風險評分
   - 需與客戶明確溝通延後原因
   - Sprint 6 需增加 56h 工時

2. **TTS 功能限制**:
   - 無法選擇語音 (系統預設)
   - 不同設備音質不同
   - iOS Safari 需用戶手勢觸發

3. **趨勢圖表可能延後**:
   - 如 Sprint 3 時間緊張，可延至 Sprint 4

---

## 🔄 替代方案 (Alternatives Considered)

### 方案 A: 硬做完所有功能 (原計劃 176h)

**優點**:
- 功能最完整
- 營養評估納入 MVP

**缺點**:
- ❌ 工時過重，延遲風險高
- ❌ 營養需求不明確，可能返工
- ❌ TTS 過度設計，浪費資源
- ❌ 團隊壓力大，品質風險

**結論**: ❌ 不採用 - 違反實用主義原則

### 方案 B: 完全移除 TTS (只做 360° + 問卷)

**優點**:
- 工時最少 (88h)
- 聚焦核心中的核心

**缺點**:
- ❌ 失去無障礙加分項
- ❌ 8h TTS 成本很低，值得做
- ❌ 錯過 Web Speech API 簡單方案

**結論**: ❌ 不採用 - TTS 簡化後值得保留

### 方案 C: 採用實用主義路線 (本方案, 96h)

**優點**:
- ✅ 聚焦核心 (360° + 問卷)
- ✅ 保留無障礙 (TTS 8h)
- ✅ 延後不明確需求 (營養)
- ✅ 工時合理，交付穩定

**缺點**:
- ⚠️ 營養評估延後
- ⚠️ TTS 功能限制

**結論**: ✅ 採用 - 平衡交付與品質

---

## 📅 執行計畫 (Implementation Plan)

### Week 5 (本週剩餘) - 32h
```
🎯 Task 5.1 - 個案 360° 頁面
├─ Day 1-2: 靜態資料顯示 [16h]
├─ Day 3: 錯誤處理與載入 [8h]
└─ Day 4: 測試與修復 [8h]
```

### Week 6 (下週) - 40h
```
🎯 Task 5.3 - LIFF 問卷頁 [24h]
├─ Day 1-2: CAT 表單 UI [12h]
├─ Day 3: mMRC + 結果顯示 [8h]
└─ Day 4: 測試 [4h]

🟢 Task 5.6 - CAT TTS [8h]
└─ Day 4: useTTS Hook + 朗讀按鈕 [8h]

🟡 Task 5.4 - 趨勢圖表 (可選) [8h]
└─ Day 5: 如有時間
```

### Sprint 6 調整
```
原計劃: AI 語音處理鏈 [88h]
調整後: AI 語音 + 營養評估 [144h]
  ├─ AI Worker 語音 [88h]
  └─ 營養評估 KPI [56h] ⭐ 從 Sprint 3 移入
```

---

## ✅ 驗收標準 (Acceptance Criteria)

### Sprint 3 完成標準 (Definition of Done)

**MUST (必須完成)**:
- ✅ Survey API 完成 (已完成)
- ⬜ 個案 360° 頁面顯示 Patient + DailyLog + Survey
- ⬜ LIFF 可填寫 CAT (8 題) 和 mMRC (1 題)
- ⬜ 問卷分數正確計算並顯示
- ⬜ 基本 TTS 朗讀功能 (CAT + mMRC)
- ⬜ 基本錯誤處理 (網路失敗、API 錯誤)
- ⬜ 手動測試通過 (治療師 + 病患角色)

**SHOULD (最好完成)**:
- ⬜ 趨勢圖表元件 (日誌 or 問卷趨勢)

**DEFERRED (明確延後)**:
- ~~營養評估 KPI~~ → Sprint 6+
- ~~AI Worker 語音~~ → Sprint 6

---

## 📚 參考資料 (References)

### 內部文檔
- WBS v3.3.0: docs/16_wbs_development_plan.md
- Changelog: docs/dev_logs/CHANGELOG_20251022.md
- 參考實現: docs/frontend/cat_form.html (無障礙設計與 TTS)

### 外部資源
- [Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [WCAG 2.1 無障礙指南](https://www.w3.org/WAI/WCAG21/quickref/)
- [Linus Torvalds on Good Taste](https://www.youtube.com/watch?v=o8NPllzkFhE)

### 相關 ADR
- ADR-011: CAT 無障礙 TTS 技術方案
- ADR-XXX: 營養評估功能設計 (Sprint 6 前創建)

---

## 💬 備註 (Notes)

### Linus 式總結

> **"Theory and practice sometimes clash. Theory loses. Every single time."**

我們做對了三件事：
1. **識別真問題** - MVP 不需要營養評估，那就不做
2. **避免過度設計** - Web Speech API 夠用就別搞複雜的
3. **聚焦交付** - 讓治療師能看病患資料，病患能填問卷，就是勝利

### 客戶溝通重點

在 Sprint 3 結束前，需與客戶明確溝通：
1. **營養評估延後原因**: 需求不明確，避免返工
2. **何時會做**: Sprint 6 (MVP 後優化期)
3. **需要客戶配合**: 明確量表、權重、指標選擇
4. **不影響 MVP 交付**: 核心功能不受影響

---

**批准**: Technical Lead, Product Manager
**生效日期**: 2025-10-22
**下次審查**: Sprint 3 結束 (2025-11-05)

---

**維護者**: RespiraAlly Development Team
**最後更新**: 2025-10-22
