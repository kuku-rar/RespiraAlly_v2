# RespiraAlly V2.0 前端專案

本目錄包含 RespiraAlly 的兩個前端應用：

## 📁 專案結構

```
frontend/
├── dashboard/          # 治療師端儀表板 (Next.js)
│   ├── app/           # App Router pages
│   ├── components/    # React components
│   ├── lib/           # Utilities (API client, utils)
│   └── styles/        # Global styles
│
└── liff/              # 病患端 LIFF 應用 (Vite + React)
    ├── src/
    │   ├── components/  # React components
    │   ├── pages/       # Page components
    │   ├── services/    # API services
    │   ├── hooks/       # Custom hooks
    │   └── utils/       # Utility functions
    └── public/          # Static assets
```

## 🚀 快速開始

### Dashboard (治療師端)

```bash
cd dashboard
npm install
npm run dev
```

- 開發伺服器: http://localhost:3000
- 構建生產版本: `npm run build`
- 啟動生產伺服器: `npm start`

**環境變數**:
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_MOCK_MODE=true
```

### LIFF (病患端)

```bash
cd liff
npm install
npm run dev
```

- 開發伺服器: http://localhost:5173
- 構建生產版本: `npm run build`
- 預覽生產版本: `npm run preview`

**環境變數**:
```bash
# .env
VITE_LIFF_ID=your_liff_id_here
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_MOCK_MODE=true
```

## 🎨 技術棧

### 共通技術
- **React 18**: UI 框架
- **TypeScript**: 類型安全
- **Tailwind CSS**: 樣式框架
- **TanStack Query**: 服務器狀態管理
- **Zustand**: 全局狀態管理
- **Axios**: HTTP 客戶端
- **Zod**: 數據驗證

### Dashboard 專屬
- **Next.js 14**: React 框架 (App Router)
- **Recharts**: 圖表庫
- **React Table**: 表格管理

### LIFF 專屬
- **Vite**: 構建工具
- **@line/liff**: LINE LIFF SDK
- **React Hook Form**: 表單管理

## 📦 API Client

兩個專案都包含統一的 API Client，支持：

- ✅ JWT 認證自動注入
- ✅ 錯誤處理與重試
- ✅ Mock 模式開發
- ✅ TypeScript 類型支持

**使用範例**:

```typescript
import { apiClient } from '@/lib/api-client' // Dashboard
// 或
import { apiClient } from '@/services/api-client' // LIFF

// GET 請求
const patients = await apiClient.get<Patient[]>('/patients')

// POST 請求
const newLog = await apiClient.post('/daily-logs', {
  water_intake: 1500,
  exercise_minutes: 30,
})
```

## 🎯 Elder-First 設計原則

LIFF 應用遵循長者優先設計：

- ✅ **大字體**: 基礎字體 18px
- ✅ **大觸控目標**: 最小 44x44px
- ✅ **高對比度**: WCAG AA 標準
- ✅ **簡化流程**: 最小化步驟
- ✅ **清晰反饋**: 明確的操作回饋

## 🧪 測試

```bash
# Dashboard
cd dashboard
npm run test

# LIFF
cd liff
npm run lint
npm run type-check
```

## 📝 開發指南

### 新增頁面

**Dashboard (App Router)**:
```bash
# 在 app/ 目錄下創建新路由
app/patients/[id]/page.tsx
```

**LIFF (File-based routing with React Router)**:
```bash
# 在 src/pages/ 目錄下創建頁面組件
src/pages/DailyLogPage.tsx
```

### 新增組件

```bash
# Dashboard
components/shared/PatientCard.tsx

# LIFF
src/components/VoiceRecorder.tsx
```

### API 整合

1. 在 `.env.local` 或 `.env` 設定 `MOCK_MODE=false`
2. 確保後端 API 正在運行
3. 使用 `apiClient` 發送請求

## 🔧 故障排除

### Port 衝突
- Dashboard 預設 port 3000
- LIFF 預設 port 5173
- 可透過 `-p` 參數指定其他 port

### 依賴問題
```bash
rm -rf node_modules package-lock.json
npm install
```

### Type 錯誤
```bash
npm run type-check
```

## 📚 相關文檔

- [前端架構規範](../docs/12_frontend_architecture_specification.md)
- [前端信息架構](../docs/17_frontend_information_architecture_template.md)
- [API 設計規範](../docs/06_api_design_specification.md)

## 🤝 貢獻指南

1. 遵循 TypeScript 嚴格模式
2. 使用 Conventional Commits
3. 提交前執行 `npm run lint`
4. 確保 type-check 通過
5. 更新相關文檔

---

**維護者**: RespiraAlly Development Team
**最後更新**: 2025-10-20
