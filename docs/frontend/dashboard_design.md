# RespiraAlly ｜ COPD 個案管理儀表板—設計規範

> 本文件定義 RespiraAlly COPD 個案管理儀表板的設計原則、UI/UX 規範、樣式定義，為前端開發提供視覺與互動標準。

---

## 一、設計原則（Style 與 UX）

- **對象**：呼吸治療師（臨床決策支援）。
- **字體與大小**：`Noto Sans TC`；基準 `18px`；KPI/標題 `20–24px`；可點擊元素最小 `44×44px`。
- **色彩（以 glassmorphism 、柔和漸變風格融合 ant-design 設計框架）**
  `--bg-top:#E9F2FF`（頂部標題底色） / `--primary:#7CC6FF` / `--purple:#CBA6FF` / `--mint:#B8F2E6` / `--danger:#E66A6A` / 文字 `#2C3E50`、輔助 `#6B7280`。
- **可用性**：高對比、明確層級、KPI 卡可掃視；圖表必有 Tooltip、Legend、空值狀態。
- **布局**：左側固定 `<nav>`、中間主內容、右側輔助欄；行動版左欄折疊為抽屜。

## 二、全域樣式（直接建立 `src/index.css` 或全域 Style 區塊）

```css
:root {
  --bg-top: #e9f2ff;
  --primary: #7cc6ff;
  --purple: #cba6ff;
  --mint: #b8f2e6;
  --danger: #e66a6a;
  --text: #2c3e50;
  --muted: #6b7280;
  --card: #ffffff;
  --shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}
body {
  font-family: "Noto Sans TC", system-ui, -apple-system, Segoe UI, Roboto,
    "PingFang TC", "Microsoft JhengHei", sans-serif;
  color: var(--text);
  background: linear-gradient(180deg, #f7faff 0%, #fdfeff 100%);
}
.header {
  background: var(--bg-top);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.card {
  background: var(--card);
  border-radius: 16px;
  box-shadow: var(--shadow);
  padding: 16px;
}
.kpi {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
}
.chart {
  min-height: 280px;
}
.nav {
  width: 240px;
  background: linear-gradient(180deg, #ecf6ff, #f7f5ff);
  padding: 16px;
}
.rightPane {
  width: 280px;
}
.btn {
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--primary);
  color: white;
  font-weight: 600;
}
.badge {
  padding: 4px 10px;
  border-radius: 99px;
  background: #eef6ff;
  color: #2563eb;
}

/* 任務管理相關樣式 */
.seg-group {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px;
  border-radius: 12px;
}
.seg-btn {
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s;
}
.seg-btn.is-active {
  background: var(--primary);
  color: white;
}
.kanban-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
.task-card {
  background: white;
  border-radius: 12px;
  padding: 12px;
  cursor: move;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.task-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
```

## 三、頁面視覺規範

### 1) 總覽頁（/overview）

- **頂部標題**：具有底色（`var(--bg-top)`），包含日期與風險篩選
- **KPI 卡片**：使用 `.kpi` 網格布局，每張卡片使用 `.card` 樣式
- **圖表區域**：統一使用 `.chart` 容器，確保最小高度
- **配色**：高風險使用 `--danger`，低依從性使用 `--purple`

### 2) 個案管理（/cases）

- **左側列表**：使用卡片式設計，懸浮效果
- **右側詳情**：資訊卡片堆疊，間距 16px
- **個案 KPI**：突出顯示關鍵指標，使用大字體
- **趨勢圖表**：小倍數設計，保持一致的軸線

### 3) 衛教資源（/education）

- **搜尋欄**：置頂固定，圓角設計
- **類別篩選**：標籤式設計，選中狀態明顯
- **問答卡片**：雙欄網格，可編輯狀態有邊框提示
- **操作按鈕**：懸浮於卡片右上角

### 4) 任務管理（/tasks）

- **檢視切換**：使用 `.seg-group` 分段控制
- **日曆檢視**：事件色塊依據任務類型
- **看板檢視**：使用 `.kanban-container` 網格
- **任務卡片**：`.task-card` 樣式，支援拖曳視覺反饋

## 四、互動設計原則

### 可及性（Accessibility）

- 所有互動元素最小尺寸 44×44px
- 對比度符合 WCAG AA 標準
- 焦點狀態明確可見
- 支援鍵盤導航

### 回饋機制

- 載入狀態：骨架屏或旋轉指示器
- 錯誤狀態：紅色邊框 + 說明文字
- 成功狀態：綠色勾選 + 淡出動畫
- 空狀態：友善插圖 + 引導文字

### 響應式設計

- 桌面版：三欄布局（導航/內容/輔助）
- 平板版：隱藏右側欄，左側欄可收合
- 手機版：單欄布局，底部導航

## 五、圖表設計規範

### 通用原則

- 統一使用 Recharts 元件庫
- 色彩遵循設計系統變數
- 必須包含 Tooltip 和 Legend
- 支援無障礙（aria-label）

### 圖表類型

1. **趨勢圖**：折線圖，支援多指標
2. **分布圖**：圓餅圖或環形圖
3. **熱力圖**：日曆格式，色階表示強度
4. **小倍數**：4 格網格，統一刻度

## 六、元件樣式指南

### 按鈕（Button）

```css
/* 主要按鈕 */
.button.primary {
  background: var(--primary);
  color: white;
}

/* 次要按鈕 */
.button.secondary {
  background: transparent;
  border: 1px solid var(--primary);
  color: var(--primary);
}

/* 危險按鈕 */
.button.danger {
  background: var(--danger);
  color: white;
}
```

### 表單元素

```css
/* 輸入框 */
.input {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 16px;
}

/* 選擇器 */
.select {
  appearance: none;
  background-image: url("data:image/svg+xml,...");
  background-position: right 12px center;
  background-repeat: no-repeat;
  padding-right: 40px;
}
```

### 卡片變體

```css
/* 玻璃擬態卡片 */
.card.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 教育卡片 */
.edu-card {
  transition: transform 0.2s;
}
.edu-card:hover {
  transform: translateY(-4px);
}
```

## 七、動畫與過渡

### 基本過渡

```css
/* 通用過渡 */
* {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-duration: 200ms;
}

/* 變形過渡 */
.transform-transition {
  transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 載入動畫

```css
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.skeleton {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  background: #e5e7eb;
}
```

## 八、深色模式考量（預留）

雖然初版不實作深色模式，但設計時應考慮：

- 使用 CSS 變數便於主題切換
- 避免硬編碼顏色值
- 圖片和圖示應有深色版本
- 對比度在兩種模式下都要足夠

## 九、效能優化建議

### 視覺效能

- 使用 CSS transform 而非 position 做動畫
- 避免大面積陰影和模糊效果
- 圖片使用適當格式（WebP/AVIF）
- 實施圖片懶加載

### 感知效能

- 使用骨架屏取代載入旋轉
- 漸進式載入（先文字後圖片）
- 樂觀更新（先更新 UI 後同步）
- 適當的載入狀態分級

## 十、設計交付規範

### 命名規範

- 色彩：`--{用途}-{強度}`
- 間距：`spacing-{size}`
- 字體：`font-{用途}`
- 陰影：`shadow-{強度}`

### 文件要求

- 每個新元件需附設計稿
- 標註間距、顏色、字體
- 提供各種狀態（正常/懸浮/按下/禁用）
- 包含響應式斷點說明

---

本設計規範為活文件，隨專案發展持續更新。所有設計決策應以提升呼吸治療師的工作效率和使用體驗為核心目標。
