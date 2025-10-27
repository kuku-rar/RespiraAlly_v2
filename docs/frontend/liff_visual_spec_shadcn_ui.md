# RespiraAlly LIFF Elder-First 視覺設計依據（shadcn UI 基底）

> 針對 LINE LIFF 輕量前端，結合 Elder-first UI/UX 原則與既有 shadcn UI token，做為高齡病患互動介面的視覺與實作指引。落點於單手可操作、資訊階層清楚、步驟不超過三層。

---

## 一、設計定位與使用情境
- **主要對象**：60+ COPD 病患與照護者，透過 LINE LIFF 進行每日症狀回報、衛教閱覽與 AI 對話。
- **操作載具**：手機為主（375~428px viewport），必須支援單手拇指操作與高亮度環境可讀性。
- **Elder-first 原則**：基礎字級 ≥ 18px、最小觸控區域 ≥ 44px、流程步驟 ≤ 3、層級清楚且語句友善、顏色對比 ≥ 4.5：1。
- **互動節奏**：以 card-based 對話容器串連核心任務，重點 CTA 使用 primary button，次要動作退居 ghost/outline，避免畫面過載。

## 二、shadcn Token 對照（對應 `frontend/liff/src/index.css`）

```css
@layer base {
  :root {
    --background: 215.5 100% 95.7%; /* #e9f2ff */
    --foreground: 210 29% 24.3%;   /* #2c3e50 */
    --card: 0 0% 100%;
    --card-foreground: 210 29% 24.3%;
    --popover: 0 0% 100%;
    --popover-foreground: 210 29% 24.3%;
    --primary: 206.1 100% 74.3%;   /* #7cc6ff */
    --primary-foreground: 0 0% 100%;
    --secondary: 264.9 100% 82.5%; /* #cba6ff */
    --secondary-foreground: 210 29% 24.3%;
    --accent: 167.6 69% 83.5%;     /* #b8f2e6 */
    --accent-foreground: 210 29% 24.3%;
    --muted: 215.5 58% 93%;
    --muted-foreground: 220 8.9% 46.1%; /* #6b7280 */
    --destructive: 0 71.3% 65.9%; /* #e66a6a */
    --destructive-foreground: 0 0% 100%;
    --border: 206.1 100% 81%;
    --input: 206.1 100% 84%;
    --ring: 206.1 100% 74.3%;
    --radius: 0.75rem; /* 12px */
  }

  body {
    font-size: 1.125rem; /* 18px */
    line-height: 1.5;
    @apply bg-background text-foreground;
    touch-action: manipulation;
    background-image: linear-gradient(180deg, #f7faff 0%, #fdfeff 100%);
  }
}
```

- `tailwind.config.ts` 中的 `fontSize` 已以 Elder-first 為基準，維持 `base = 18px`，`lg = 20px`，`xl = 24px`。
- 建議新增 `boxShadow.card = '0 12px 28px rgba(44, 62, 80, 0.12)'` 供卡片與對話泡泡使用，減少汙濁投影。
- 日間模式優先，夜間模式待醫療合規評估後導入。

## 三、LIFF IA 對應的主要畫面

### 1) 今日任務首頁（`/`）
- **頂部問候**：使用 `Card` + `gradient` 背景呈現連續性訊息：問候語、當日日期、回報狀態。
- **任務卡片**：採 `Stacked Card`，每張卡片主標（20px）+ 說明文字（16px），右側顯示指示 icon。緊急任務使用 `--destructive` 後景淡色塊。
- **操作 CTA**：主行動 `Button` 需佔據整寬（≥320px），高度 48px；備選動作置於 `plain` 按鈕或 `Link`.
- **進度指標**：使用 `Progress` 或 `Badge` 顯示今日完成度，維持 90% 以上可讀性。

### 2) 症狀回報流程（`/survey`）
- **流程限制**：最多三個步驟，每步顯示目前位置（Step 1/3），下方提供 `Back`／`Next` 按鈕。
- **輸入元件**：
  - 單選題使用 `Segmented Control`（Button Group），最少 48x48px。
  - 數值輸入採 `NumberInput` + `Stepper`，每格 56px 寬，搭配語音輸入提示。
  - 開放文字以 `Textarea`，自動高亮輪廓。
- **錯誤提示**：紅色 `--destructive` 字體，顯示在欄位下方 14px 字級，加上 icon 提醒。
- **確認頁**：最後一步提供摘要卡，列出各題答案，可再次返回修改。

### 3) AI 對話 / 衛教（`/chat`）
- **訊息泡泡**：使用 `Card` 變體，患者端（右側）使用 `--primary` 背景，AI 端（左側）使用 `--card` + 陰影。
- **字體與排版**：聊天字級維持 18px，段落行距 1.6。重要衛教資訊以 `Callout` 結構呈現。
- **快捷建議**：以 `Chips`（ghost button）呈現常用句提示，至少 48px 高。
- **語音輔助**：語音按鈕採 `Circle Button`，80px 直徑，置底固定，使用 `--primary` 背景。

### 4) 任務歷史 / 設定（`/history`, `/settings`）
- 使用 `Accordion` 或 `Tabs` 分層顯示歷史紀錄，避免長列表。
- 列表項目卡片需提供日期、症狀摘要與醫師指示，並支援展開細節。
- 設定選項字體維持 18px，關鍵開關使用 `Switch`（加大滑塊），搭配語句式說明。

## 四、元件樣式規範

### 按鈕（Button）
- Primary：`bg-[hsl(var(--primary))] text-white hover:bg-[#69b9f7]`
- Secondary：`bg-white text-[hsl(var(--foreground))] border border-[rgba(44,62,80,0.12)]`
- Ghost：`bg-transparent text-[hsl(var(--foreground))] hover:bg-[rgba(124,198,255,0.12)]`
- Danger：`bg-[hsl(var(--destructive))] text-white hover:bg-[#d85858]`
- 所有按鈕 `min-height: 48px`、`rounded-[var(--radius)]`，`focus-visible:ring-2 ring-offset-1`.

### 表單欄位
- Input/Select：`h-14 px-4 rounded-[var(--radius)] border border-[hsl(var(--border))]`
- Placeholder：`text-[rgba(107,114,128,0.8)]`
- Focus：`ring-2 ring-offset-0 ring-[rgba(124,198,255,0.6)]`
- 錯誤狀態：`border-[hsl(var(--destructive))] text-[hsl(var(--destructive))]`

### 卡片與佈局
- Card：`rounded-xl shadow-card border border-[rgba(124,198,255,0.18)]`
- 詢問/提醒卡採 `flex gap-3 items-start`，icon 最低 28px。
- 分隔線使用 `Divider`，顏色 `rgba(107,114,128,0.35)`，厚度 1px。

### 輔助元件
- Badge：預設背景 `rgba(124,198,255,0.18)`、文字 `--primary`，活躍 Badge 使用 `--secondary`。
- Tooltip：字級 16px、內距 12px，顏色 `#2c3e50` 背景 + 白字。
- Toast：佔滿寬度，字級 18px，保留 4 秒，支援語音播報。

## 五、互動與動效
- Transition：`transition-all 200ms` 基本過場。
- Card hover：`translate-y-[-2px] shadow-lg`.
- Skeleton：`bg-[#e5edf7] animate-pulse`，補上語音提示（待研議）。
- Loading：按鈕載入時顯示 spinner（24px）搭配 `aria-live="polite"`。

## 六、可用性與無障礙
- 對比檢查：主要文字對背景需達 4.5:1；主行動按鈕與背景 6:1。
- 語音優先：提供 `aria-label`、支援 LINE 字幕與 TTS。
- 針對手部抖動：關鍵按鈕間距 ≥ 12px，避免誤觸。
- 表單支援「快捷選項 + 語音輸入 + 手動輸入」三種模式，使用者可自由切換。

## 七、實作建議與資源
- Tailwind layer 建議新增：

```css
@layer components {
  .btn-primary { @apply h-12 w-full rounded-[var(--radius)] bg-primary text-primary-foreground font-semibold; }
  .card-elevated { @apply rounded-xl border border-[rgba(124,198,255,0.18)] shadow-card bg-card; }
  .field-base { @apply h-14 rounded-[var(--radius)] border border-[hsl(var(--border))] px-4 text-base; }
}
```

- 響應式策略：小尺寸維持單欄排版；平板以上可以二欄呈現歷史資訊，但保留 44px click area。
- 圖像資源：使用向量插圖或 Lucide icon（線性 24px），確保縮放不失真。

## 八、文件維運
- 此規範與 `dashboard_design_shadcn_ui.md` 共同維護色彩與語意 token；若 token 調整需同步更新兩份文件與 `tailwind.config.ts`。
- 建議新增 `design-tokens.md`（全域），追蹤跨應用的 token 與版本差異。
- 每次釋出前請 QA 依 Elder-first 清單驗證：字級、觸控尺寸、流程步驟、對比度。

---

本文件協助 LIFF 前端在延續 shadcn UI 風格的前提下，確保高齡病患操作無障礙，並降低雙端樣式分歧風險。
