# RespiraAlly COPD 管理儀表板 shadcn UI 設計依據

> 依循既有資訊架構與功能需求，導入 shadcn UI 設計語彙與原子化樣式，作為重新風格化儀表板前的視覺與互動依據，確保體驗一致且可快速落地開發。

---

## 一、設計精神（Style 與 UX）
- **風格定位**：以 shadcn UI 的極簡、實用風格為底，結合醫療情境下的安心、信任感，整體氛圍採柔和清透、線條俐落的卡片式布局。
- **組件語彙**：主要使用 shadcn UI 的 `Card`、`Button`、`Tabs`、`Badge`、`Dialog`、`Sheet`、`Dropdown Menu`、`Tooltip` 等元件，維持統一的邊角、陰影與互動節奏。
- **字體與排版**：繁體中文優先使用 `Noto Sans TC`，英數輔以 `Inter`。文字階層維持 H1 28px、H2 22px、H3 18px、正文 16px、輔助文字 14px，字距採 shadcn 預設的 1.4 line-height。
- **色彩基調**：以使用者提供的色票為品牌基底，區分主色（--primary）、強調色（--purple）、成功色（--mint）、警示色（--danger），搭配柔和背景（--bg-top）與卡片白（--card）。
- **互動準則**：所有可操作元素使用 shadcn UI 預設的 hover/focus ring 範例，加上清楚的狀態標記與 Tooltip 提示，避免重新設計互動模式造成學習成本。

## 二、系統樣式建議：基底 Style 變數（對應 `frontend/dashboard/app/globals.css`，同步於 `docs/frontend/liff_visual_spec_shadcn_ui.md`）

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 215.5 100% 95.7%; /* #e9f2ff */
    --foreground: 210 29% 24.3%; /* #2c3e50 */
    --card: 0 0% 100%;
    --card-foreground: 210 29% 24.3%;
    --popover: 0 0% 100%;
    --popover-foreground: 210 29% 24.3%;
    --primary: 206.1 100% 74.3%; /* #7cc6ff */
    --primary-foreground: 0 0% 100%;
    --secondary: 264.9 100% 82.5%; /* #cba6ff */
    --secondary-foreground: 210 29% 24.3%;
    --accent: 167.6 69% 83.5%; /* #b8f2e6 */
    --accent-foreground: 210 29% 24.3%;
    --muted: 215.5 58% 93%;
    --muted-foreground: 220 8.9% 46.1%; /* #6b7280 */
    --destructive: 0 71.3% 65.9%; /* #e66a6a */
    --destructive-foreground: 0 0% 100%;
    --border: 206.1 100% 81%;
    --input: 206.1 100% 84%;
    --ring: 206.1 100% 74.3%;
    --radius: 1rem; /* 16px */
    --bg-top: #e9f2ff;
    --shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  }

  .dark {
    --background: 216.9 54.2% 9.4%; /* #0b1525 */
    --foreground: 210 40% 98%;
    --card: 216.9 54.2% 12%;
    --card-foreground: 210 40% 98%;
    --popover: 216.9 54.2% 12%;
    --popover-foreground: 210 40% 98%;
    --primary: 206.1 100% 74.3%;
    --primary-foreground: 216.9 54.2% 12%;
    --secondary: 264.9 100% 82.5%;
    --secondary-foreground: 216.9 54.2% 12%;
    --accent: 167.6 69% 67%;
    --accent-foreground: 216.9 54.2% 12%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --destructive: 0 62% 50%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 206.1 100% 74.3%;
    --shadow: 0 12px 32px rgba(12, 20, 35, 0.42);
  }

  body {
    @apply bg-background text-foreground;
    font-family: "Noto Sans TC", "Inter", "Segoe UI", sans-serif;
    background-image: linear-gradient(180deg, var(--bg-top) 0%, #fdfeff 100%);
  }
}

/* LIFF 共用 tokens（詳見 docs/frontend/liff_visual_spec_shadcn_ui.md） */
:root {
  --liff-radius: 0.75rem;
  --liff-card-shadow: 0 12px 28px rgba(44, 62, 80, 0.12);
}

.shad-card {
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  box-shadow: var(--shadow);
}

.shad-highlight {
  background: rgba(124, 198, 255, 0.12);
  border: 1px solid rgba(124, 198, 255, 0.35);
}
```

- Tailwind 設定：於 `frontend/dashboard/tailwind.config.ts` 的 `extend.colors` 中確保 `primary.foreground` 對應 `hsl(var(--primary-foreground))`、`card.foreground` 對應 `hsl(var(--card-foreground))`，並加入 `accent`、`secondary`、`muted` 等語意顏色；`boxShadow` 中新增 `card: 'var(--shadow)'`，並與 LIFF 端 (`--liff-card-shadow`) 保持語意一致。

```ts
extend: {
  colors: {
    primary: {
      DEFAULT: 'hsl(var(--primary))',
      foreground: 'hsl(var(--primary-foreground))',
    },
    secondary: {
      DEFAULT: 'hsl(var(--secondary))',
      foreground: 'hsl(var(--secondary-foreground))',
    },
    accent: {
      DEFAULT: 'hsl(var(--accent))',
      foreground: 'hsl(var(--accent-foreground))',
    },
    muted: {
      DEFAULT: 'hsl(var(--muted))',
      foreground: 'hsl(var(--muted-foreground))',
    },
    destructive: {
      DEFAULT: 'hsl(var(--destructive))',
      foreground: 'hsl(var(--destructive-foreground))',
    },
    card: {
      DEFAULT: 'hsl(var(--card))',
      foreground: 'hsl(var(--card-foreground))',
    },
    border: 'hsl(var(--border))',
    input: 'hsl(var(--input))',
    ring: 'hsl(var(--ring))',
  },
  borderRadius: {
    lg: 'var(--radius)',
    md: 'calc(var(--radius) - 4px)',
    sm: 'calc(var(--radius) - 8px)',
  },
  boxShadow: {
    card: 'var(--shadow)',
  },
}
```

- 自訂工具類：建議在 `@layer components` 中建立 `bg-card-gradient`（覆蓋 header 背景）、`text-muted`、`border-soft` 等常用 class，以減少重複宣告。
- Dark mode：沿用 shadcn UI 的 class-based 模式，上述變數在 `.dark` 節點覆寫，可配合實際數據視覺微調亮度與對比；LIFF 夜間模式待醫療合規後同步調整。

## 三、儀表板資訊架構

### 1) 概覽區 /overview
- **主要視覺**：Header 採 `Card` + `Gradient` 背景，呈現使用者問候、重要 KPI 與即時提醒，右側配置 `Button`（primary）與 `Dropdown` 快捷操作。
- **KPI 區塊**：使用四欄 `Grid` + `Card`，內含 `Badge` 標籤、主要數值、趨勢百分比與 mini sparkline。KPI 顏色：主指標採 `--primary`，成長趨勢正向使用 `--mint`，負向使用 `--danger`。
- **圖表模組**：核心採 `Card` + shadcn `Tabs` 切換趨勢週期；圖表背景使用 `rgba(255,255,255,0.85)` 玻璃質感，維持陰影與圓角一致。
- **提醒區**：採 `Alert` 元件呈現緊急程度，danger 變體搭配深色文字與 icon，支援 `Dismiss`。

### 2) 病例管理 /cases
- **清單呈現**：以 `Data Table` 元件顯示病例分層資訊；表頭保持吸附效果，支援 `Column Visibility`、`Filter` 與 `Row Expansion`。
- **篩選器**：左側使用 `Accordion` 展開多層篩選條件，主動狀態高亮 `--primary`，次要狀態用 `--purple`。
- **病例概覽卡**：使用 `Card` + `Avatar` + `Badge` 表示風險群組，卡片 hover 時加上 `translate-y` -2px 與強化陰影。
- **重點動作**：使用 `Dropdown Menu` 避免主畫面過度擁擠，重要操作（如建立追蹤）使用 primary button 固定在右上角。

### 3) 教育資源 /education
- **內容卡**：採雙欄 `Grid` + `Card`，Card 頂部使用 `Aspect Ratio` 顯示圖片或影音縮圖，內文搭配 `Badge` 表示主題。
- **分類導覽**：使用 `Tabs` 或 `Segmented Control` 切換常見議題、最新更新、醫師推薦等分類，active 狀態用 `--purple`。
- **互動元素**：支援 `Dialog` 開啟全文與 `Sheet` 進行快速分享。CTA 按鈕使用 `ghost` 變體以降低視覺重量。

### 4) 任務追蹤 /tasks
- **看板布局**：`Kanban` 欄位使用 `Card` 組合，欄位標題包含 `Badge` 顯示任務數，欄底提供新增任務的 `ghost` button。
- **拖曳回饋**：採 `react-beautiful-dnd` 或同款庫，拖曳時卡片陰影加深並顯示 `outline`，落點有淡色 Feedback。
- **任務內容**：Card 內含 `Checkbox`、到期日 `Badge` 與 `Avatar Group`；逾期任務日期改用 `--danger` 前景。
- **右側摘要**：右欄保留 `Card` 顯示工作量統計、逾期率與提醒清單，支援 `Collapse` 收合。

## 四、視覺設計準則

### 易用性（Accessibility）
- 對比比例至少達 4.5:1，Primary 與 Danger 按鈕需加入深色字或陰影以確保可讀性。
- Hover/Focus 狀態使用 shadcn 預設的 `ring-2 ring-offset-2`，ring 顏色以 `rgba(124, 198, 255, 0.5)`。
- 圖表與 KPI 小組件加入文字數值與 `Tooltip` 作為視覺備援，確保輔助科技可讀取。

### 圓角與陰影
- Card 與 Dialog 使用 `16px` 圓角，一致使用 `--shadow`。較大的模組（例如主要圖表）可升級為 `--radius-lg`（24px）營造核心模組層級。
- 懸浮按鈕、Chip 使用 `var(--radius-sm)`，避免過度圓角造成醫療場域過於遊戲化。

### 版面節奏
- Layout 採 12 欄 Grid，左右內距 24px、模組間距 16px。區段間（如 Overview 與 Cases）以 32px 間距分隔。
- 使用 shadcn 的 `Separator` 分隔次要資訊，避免使用過多邊框。

## 五、圖表設計準則

### 調色
- 折線圖：主線使用 `--primary`，輔線使用 `#9bd6ff`；目標線採 `--purple` 的虛線。填充區域透明度 12%。
- 長條圖：正向數據採 `--mint`，負向或警示數據使用 `--danger`。
- 面積圖背景使用 `linear-gradient`，避免顏色過度飽和，同時加上 1px 邊框強化對比。

### 互動狀態
- Tooltip 採 `Popover` 樣式，內含清楚標籤與單位；資料點 hover 時使用 `scale(1.15)` 並顯示外圈 ring。
- 提供空狀態、載入狀態與無資料狀況，空狀態搭配插圖與引導按鈕。

## 六、核心元件樣式

### 按鈕（Button）
- Primary：背景 `var(--primary)`、文字白，hover 降低 4% 亮度，focus ring 使用 `rgba(124, 198, 255, 0.45)`。
- Secondary：背景白 + 邊框 `rgba(44, 62, 80, 0.12)`，hover 時變為 `rgba(124, 198, 255, 0.08)`。
- Ghost：背景透明、文字 `var(--text)`，hover 時加上淡藍底色。
- Danger：背景 `var(--danger)`，hover 時加深至 `#d85858`，禁用狀態降低透明度至 60%。
- 範例如下：

```ts
const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
  {
    variants: {
      variant: {
        primary: "bg-[var(--primary)] text-white hover:bg-[#69b9f7] focus-visible:ring-[rgba(124,198,255,0.45)]",
        secondary: "bg-white text-[var(--text)] border border-[rgba(44,62,80,0.12)] hover:bg-[rgba(124,198,255,0.08)]",
        ghost: "bg-transparent text-[var(--text)] hover:bg-[rgba(124,198,255,0.12)]",
        danger: "bg-[var(--danger)] text-white hover:bg-[#d85858] focus-visible:ring-[rgba(230,106,106,0.45)]",
      },
    },
    defaultVariants: {
      variant: "primary",
    },
  }
);
```

### 欄位樣式（Form Field）
- Input、Select、Textarea 採 `rounded-lg border border-[rgba(44,62,80,0.16)]`，Focus ring 使用 `ring-1 ring-[rgba(124,198,255,0.6)]`。
- Placeholder 顏色 `rgba(107, 114, 128, 0.8)`，錯誤狀態邊框改為 `var(--danger)` 並顯示 `FormMessage`。
- 多步驟表單採`Stepper` + `Card` 展示，步驟標記使用 `Badge`（primary/danger）。

### 資訊卡（Card）
- 頂部可附圖或 Icon 的 Card 使用 `flex gap-3` 排列，內含數值時輔以上標（Trend）。
- 精選卡片（例如病患重點）使用 `border: 2px solid rgba(203, 166, 255, 0.45)`，以區別於一般資訊卡。

## 七、微動效與過場

### 基礎過場
- 全域 transition：`transition-property: color, background-color, border-color, box-shadow; transition-duration: 200ms;`.
- 卡片 hover 增加 `translateY(-2px)` 與陰影 12px，以表達層級變化。

### 載入狀態
- Skeleton 採 `bg-[#e5edf7]`，動畫使用 `pulse`（2s）或 `shimmer`（線性漸層橫移）。
- 圖表載入：以 `Card` 內覆蓋 `Spinner` 或 skeleton bar，避免版面跳動。

## 八、前端實作需留意

### 佈局實作
- 使用 `Container` 封裝頁面最大寬度 1440px，並搭配 `Grid` + `flex` 以實現主內容與側欄。
- 小尺寸裝置時，Overview 的 KPI 改為兩欄，病患列表改為 `Accordion` 展開詳細資訊。

### 性能與狀態
- 儀表板資料採用 `SWR/React Query` 快取並顯示同步狀態，搭配 `Toast` 告知更新結果。
- 大型清單使用虛擬化（`@tanstack/react-virtual`）以維持流暢度。

### 資源管理
- 圖片採用 WebP/AVIF，並以 `next/image` 或類似優化載入。
- Icons 使用 `lucide-react`，若需自訂醫療圖示，統一以 20px 線性圖示為基準。

## 九、設計命名規範

### 命名規則
- 色票：`--{語意}-{狀態}`，例如 `--primary-hover`、`--danger-muted`。
- 間距：以 `space-{值}` 命名（px 單位），如 `space-16 = 16px`。
- 字級：`font-{層級}`，例如 `font-title-xl`、`font-body`.
- 陰影：`shadow-{層級}`，例如 `shadow-card = var(--shadow)`、`shadow-float = 0 16px 40px rgba(124,198,255,0.18)`.

### 實作要求
- 所有 token 先在 `globals.css` 或 `tailwind.config.js` 宣告，再於組件透過 `className` 調用，避免硬編碼。
- 建立 `design-tokens.md` 追蹤 token 變更，確保設計與開發同步。
- 互動狀態需提供 `default / hover / focus-visible / disabled` 四種，以便 shadcn UI `variants` 擴充。

---

本設計依據提供視覺基準與開發指引，後續可依此產出高保真稿與組件庫對照，以降低重構風險並維持使用體驗一致性。
- **跨平台一致性**：與 LIFF 視覺規範 (`docs/frontend/liff_visual_spec_shadcn_ui.md`) 共用色票、語意命名與 Elder-first 原則，以維持病患端與儀表板端的品牌識別。
