# Sprint 3 階段性開發計畫 (Week 5-6)

**版本**: v1.0
**日期**: 2025-10-22
**狀態**: 執行中 (In Progress)
**Sprint 目標**: 完成個案 360° 頁面、LIFF 問卷系統、基礎 TTS 無障礙功能

---

## 📊 Sprint 3 總覽

### 專案狀態

| 項目 | 數值 |
|------|------|
| **Sprint 工時** | 96h (已完成 56h, 剩餘 40h) |
| **Sprint 進度** | 58.3% (Task 5.2 ✅ + Task 5.1 基本完成 ✅) |
| **目標完成率** | 100% (Week 6 結束) |
| **當前週次** | Week 5 (Sprint 3 進行中) |

### 任務優先級 (基於 ADR-010)

| 任務 | 工時 | 優先級 | 狀態 | ADR 參考 |
|------|------|--------|------|----------|
| 5.1 個案 360° 頁面 | 32h | **P0** (核心) | ✅ (5.1.1-5.1.2, 5.1.4 完成) | ADR-012 |
| 5.2 CAT/mMRC 問卷 API | 24h | **P0** (核心) | ✅ | - |
| 5.3 LIFF 問卷頁 | 24h | **P0** (核心) | ⬜ | ADR-012 |
| 5.6 CAT TTS | 8h | **P1** (加分) | ⬜ | ADR-011, ADR-012 |
| 5.4 趨勢圖表元件 | 16h | **P2** (可選) | ⏭️ (延後) | - |

---

## 🗓️ Week 5 開發計畫 (本週剩餘, 32h)

### 目標：完成 Task 5.1 個案 360° 頁面

**交付物**：治療師可查看病患完整健康資料（基本資料 + 日誌趨勢 + 問卷結果）

---

### 📅 Day 1-2 (16h): 基礎架構 + API 整合

#### 🎯 目標
建立 PatientDetailPage 基礎架構，整合後端 API (Patient, DailyLog, Survey)

#### 📋 任務清單

**1. 建立 TanStack Query Hooks** [4h]

**檔案**: `frontend/dashboard/src/hooks/api/`

```bash
# 創建 Hooks 檔案
mkdir -p frontend/dashboard/src/hooks/api
touch frontend/dashboard/src/hooks/api/usePatient.ts
touch frontend/dashboard/src/hooks/api/useDailyLogs.ts
touch frontend/dashboard/src/hooks/api/useSurveys.ts
touch frontend/dashboard/src/hooks/api/index.ts
```

**實現步驟**：
1. 實現 `usePatient(patientId)` - 獲取病患基本資料
2. 實現 `useDailyLogs(patientId, options)` - 獲取日誌列表 (支持 limit 參數)
3. 實現 `useSurveys(patientId)` - 獲取問卷列表
4. 配置 Query Keys 與 Cache Time
5. 錯誤處理與 Retry 策略

**參考**: ADR-012 § 5.1.4 TanStack Query Hooks

---

**2. 建立 API Client 配置** [2h]

**檔案**: `frontend/dashboard/src/lib/api-client.ts`

**實現步驟**：
1. 配置 Axios Instance (baseURL, timeout)
2. 實現 Request Interceptor (添加 JWT Token)
3. 實現 Response Interceptor (統一錯誤處理)
4. TypeScript 類型定義 (Patient, DailyLog, Survey)

```typescript
// frontend/dashboard/src/lib/api-client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: 添加 JWT Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: 錯誤處理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 過期，跳轉登入頁
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

**3. 建立 PatientDetailPage 路由** [4h]

**檔案**: `frontend/dashboard/src/app/patients/[id]/page.tsx`

**實現步驟**：
1. 創建 Next.js 動態路由 `[id]`
2. 使用 `useParams()` 獲取病患 ID
3. 調用 TanStack Query Hooks 獲取數據
4. 實現 Loading / Error / Success 三種狀態
5. 基礎 Layout (Header + Tabs 占位符)

**參考**: ADR-012 § 5.1.3.A PatientDetailPage

---

**4. 實現 TypeScript 類型定義** [2h]

**檔案**: `frontend/dashboard/src/types/api.ts`

**實現步驟**：
1. 定義 `Patient` 介面 (與後端 Schema 一致)
2. 定義 `DailyLog` 介面
3. 定義 `Survey` 介面 (CAT, mMRC)
4. 定義 API Response 類型 (含 pagination)

```typescript
// frontend/dashboard/src/types/api.ts
export interface Patient {
  user_id: string;
  full_name: string;
  date_of_birth: string;
  gender: 'male' | 'female';
  height_cm: number;
  weight_kg: number;
  phone?: string;
  emergency_contact?: string;
  risk_level?: 'LOW' | 'MODERATE' | 'HIGH';

  // Computed fields (from backend)
  age: number;
  bmi: number;

  created_at: string;
  updated_at: string;
}

export interface DailyLog {
  log_id: string;
  patient_id: string;
  log_date: string;
  medication_taken: boolean;
  water_ml: number;
  exercise_minutes: number;
  cigarette_count: number;
  sleep_hours?: number;
  notes?: string;
  created_at: string;
}

export interface Survey {
  survey_id: string;
  patient_id: string;
  survey_type: 'CAT' | 'mMRC';
  total_score: number;
  severity?: 'MILD' | 'MODERATE' | 'SEVERE' | 'VERY_SEVERE';
  is_concerning: boolean;
  submitted_at: string;
  answers: Array<{
    question_id: number;
    answer: number;
  }>;
}
```

---

**5. 手動測試 API 整合** [4h]

**測試項目**：
- [ ] `GET /patients/{id}` 正確返回病患資料
- [ ] `GET /daily-logs/patient/{id}?limit=7` 返回最近 7 天日誌
- [ ] `GET /surveys/patient/{id}` 返回問卷列表
- [ ] Loading 狀態正確顯示 (Spinner)
- [ ] Error 狀態正確顯示 (錯誤訊息 + 重試按鈕)
- [ ] 數據正確渲染到頁面 (console.log 驗證)

**預期輸出**：PatientDetailPage 可正確獲取並顯示 API 數據（暫時以 JSON 格式顯示）

---

### 📅 Day 2-3 (12h): 核心組件實現

#### 🎯 目標
實現 PatientHeader 與 PatientTabs 組件，顯示病患基本資料與 Tab 切換

#### 📋 任務清單

**1. 實現 PatientHeader 組件** [4h]

**檔案**: `frontend/dashboard/src/components/patient/PatientHeader.tsx`

**實現步驟**：
1. 設計 Layout (Avatar + Info + Actions)
2. 顯示病患姓名、年齡、性別、BMI
3. 顯示風險等級 Badge (LOW/MODERATE/HIGH)
4. 實現 Action Buttons (發送訊息、編輯資料 - 暫時僅 UI)
5. 響應式設計 (Desktop + Tablet)

**參考**: ADR-012 § 5.1.3.B PatientHeader

**UI 檢查清單**：
- [ ] Avatar 顯示姓名首字母
- [ ] 年齡自動計算 (從 date_of_birth)
- [ ] BMI 顯示小數點 1 位
- [ ] 風險等級 Badge 顏色正確 (綠/黃/紅)
- [ ] 按鈕 Hover 效果正常

---

**2. 實現 PatientTabs 組件** [4h]

**檔案**: `frontend/dashboard/src/components/patient/PatientTabs.tsx`

**實現步驟**：
1. 使用 shadcn/ui Tabs 組件
2. 實現三個 Tab: 概覽、日誌歷史、問卷歷史
3. 概覽 Tab: 健康摘要卡片 + 趨勢圖表占位符 + 最新問卷
4. 日誌 Tab: 日誌列表占位符
5. 問卷 Tab: 問卷列表占位符

**Tab 結構**：
```tsx
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">概覽</TabsTrigger>
    <TabsTrigger value="logs">日誌歷史</TabsTrigger>
    <TabsTrigger value="surveys">問卷歷史</TabsTrigger>
  </TabsList>

  <TabsContent value="overview">
    {/* HealthSummaryCard + Trend Chart + LatestSurvey */}
  </TabsContent>

  <TabsContent value="logs">
    {/* DailyLogsTable (Day 3) */}
  </TabsContent>

  <TabsContent value="surveys">
    {/* SurveysHistory (Day 3) */}
  </TabsContent>
</Tabs>
```

---

**3. 實現 HealthSummaryCard 組件** [4h]

**檔案**: `frontend/dashboard/src/components/patient/HealthSummaryCard.tsx`

**實現步驟**：
1. 顯示最新日誌的健康指標 (飲水、運動、用藥)
2. 使用 MetricCard 子組件 (Icon + Label + Value + Unit)
3. 計算 7 天平均值
4. 無數據時顯示 "暫無資料"

**UI 範例**：
```
┌─────────────────────────────────────┐
│  今日健康摘要                        │
├─────────────────────────────────────┤
│  💧 飲水量        1500 ml           │
│  🏃 運動時間       30 分鐘          │
│  💊 用藥狀態       已服用           │
└─────────────────────────────────────┘
```

**數據來源**: `useDailyLogs(patientId, { limit: 1 })` 獲取最新日誌

---

### 📅 Day 3 (8h): 資料視覺化組件

#### 🎯 目標
實現 DailyLogsTrendChart 趨勢圖表，顯示 7 天健康指標變化

#### 📋 任務清單

**1. 實現 DailyLogsTrendChart 組件** [6h]

**檔案**: `frontend/dashboard/src/components/patient/DailyLogsTrendChart.tsx`

**實現步驟**：
1. 安裝 Recharts: `npm install recharts`
2. 轉換 DailyLog[] 為 Chart Data 格式
3. 實現 LineChart (X軸: 日期, Y軸: 數值)
4. 支持指標切換 (飲水量 / 運動時間 / 用藥依從)
5. 響應式設計 (ResponsiveContainer)

**參考**: ADR-012 § 5.1.3.C DailyLogsTrendChart

**UI 檢查清單**：
- [ ] 圖表正確顯示 7 天數據
- [ ] X 軸日期格式正確 (MM/DD)
- [ ] Y 軸數值範圍自動調整
- [ ] 指標切換按鈕正常
- [ ] Tooltip 顯示詳細數據

---

**2. 實現 LatestSurveyCard 組件** [2h]

**檔案**: `frontend/dashboard/src/components/patient/LatestSurveyCard.tsx`

**實現步驟**：
1. 獲取最新 CAT/mMRC 問卷
2. 顯示分數、嚴重度、提交日期
3. 分數 Badge 顏色 (綠/黃/紅)
4. 點擊查看詳情 (導向問卷 Tab)

**UI 範例**：
```
┌─────────────────────────────────────┐
│  最新 CAT 問卷                       │
├─────────────────────────────────────┤
│  總分: 15 分  🟡 中度                │
│  提交時間: 2025-10-22 14:30         │
│  [ 查看詳情 ]                        │
└─────────────────────────────────────┘
```

**數據來源**: `useSurveys(patientId)` 取第一筆 (最新)

---

### 📅 Day 4 (8h): 錯誤處理 + 測試 + 優化

#### 🎯 目標
完善錯誤處理、實現組件測試、性能優化

#### 📋 任務清單

**1. 錯誤處理與 Loading 狀態** [3h]

**實現步驟**：
1. 實現 LoadingSpinner 組件 (全頁 + 局部)
2. 實現 ErrorAlert 組件 (帶重試按鈕)
3. 實現 EmptyState 組件 (無數據時顯示)
4. 在所有 API 調用處添加錯誤處理
5. 實現 ErrorBoundary (捕獲組件錯誤)

**測試項目**：
- [ ] API 失敗時顯示錯誤訊息
- [ ] 重試按鈕功能正常
- [ ] Loading 狀態不閃爍 (min-height)
- [ ] 無數據時顯示友善提示

---

**2. 組件單元測試** [3h]

**工具**: Vitest + Testing Library

**測試檔案**：
- `PatientHeader.test.tsx`
- `HealthSummaryCard.test.tsx`
- `DailyLogsTrendChart.test.tsx`

**測試案例**：
```typescript
// PatientHeader.test.tsx
describe('PatientHeader', () => {
  it('正確顯示病患姓名與年齡', () => {
    const patient = { full_name: '王小明', age: 65, ... };
    render(<PatientHeader patient={patient} />);
    expect(screen.getByText('王小明')).toBeInTheDocument();
    expect(screen.getByText('65 歲')).toBeInTheDocument();
  });

  it('高風險病患顯示紅色 Badge', () => {
    const patient = { risk_level: 'HIGH', ... };
    render(<PatientHeader patient={patient} />);
    const badge = screen.getByText('高風險');
    expect(badge).toHaveClass('bg-red-500');
  });
});
```

**目標覆蓋率**: ≥ 80%

---

**3. 性能優化** [2h]

**優化項目**：
1. 實現 React.memo 避免不必要渲染
2. 圖表組件 Lazy Loading
3. 圖片優化 (Next.js Image)
4. 代碼分割 (Dynamic Import)

**檢查清單**：
- [ ] Lighthouse Performance Score ≥ 90
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1

---

### ✅ Week 5 驗收標準

**功能驗收**：
- [ ] PatientDetailPage 正確顯示病患基本資料
- [ ] 顯示最新 7 天日誌趨勢圖 (飲水、運動、用藥)
- [ ] 顯示最新問卷結果 (CAT/mMRC)
- [ ] Tab 切換功能正常
- [ ] 錯誤狀態與 Loading 狀態正確

**技術驗收**：
- [ ] TanStack Query 正確管理 API 狀態
- [ ] TypeScript 無錯誤
- [ ] 組件測試覆蓋率 ≥ 80%
- [ ] Lighthouse Performance ≥ 90
- [ ] 響應式設計 (Desktop + Tablet)

---

## 🗓️ Week 6 開發計畫 (下週, 40h)

### 目標：完成 Task 5.3 LIFF 問卷頁 + Task 5.6 TTS

**交付物**：病患可在 LINE LIFF 填寫 CAT/mMRC 問卷 + TTS 語音朗讀

---

### 📅 Day 1 (8h): LIFF 基礎架構 + useTTS Hook

#### 🎯 目標
建立 LIFF 專案基礎架構，實現 useTTS Hook

#### 📋 任務清單

**1. LIFF 專案環境檢查** [1h]

**實現步驟**：
1. 檢查 Vite + React 專案配置
2. 確認 LIFF SDK 已安裝
3. 配置環境變數 (LIFF ID)
4. 測試 LIFF 初始化流程

```bash
# 檢查 LIFF SDK
cd frontend/liff
npm list @line/liff

# 如未安裝
npm install @line/liff
```

---

**2. 實現 useTTS Hook** [4h] ⭐ ADR-011

**檔案**: `frontend/liff/src/hooks/useTTS.ts`

**實現步驟**：
1. 檢查 Web Speech API 支援度
2. 實現 speak(text) 方法
3. 實現 stop() 方法
4. 管理 isSpeaking 狀態
5. 配置繁體中文語音 (zh-TW)
6. 設定老年人友善語速 (0.9x)

**參考**: ADR-012 § 5.3.3.B useTTS Hook, ADR-011

**測試項目**：
- [ ] iOS Safari 語音正常 (需用戶手勢觸發)
- [ ] Android Chrome 語音正常
- [ ] 語速正確 (0.9x)
- [ ] 中文發音清晰
- [ ] isSpeaking 狀態正確

---

**3. 實現 SurveyPage 基礎架構** [3h]

**檔案**: `frontend/liff/src/pages/SurveyPage.tsx`

**實現步驟**：
1. 實現問卷狀態管理 (useState)
   - currentQuestion: number
   - answers: Record<number, number>
   - isComplete: boolean
2. 整合 useTTS Hook
3. 實現問題切換邏輯
4. 實現分數計算邏輯
5. 基礎 Layout (Header + Question Card 占位符)

**參考**: ADR-012 § 5.3.3.A SurveyPage

---

### 📅 Day 2 (8h): CAT 問卷 UI 實現

#### 🎯 目標
實現 CAT 8 題問卷 UI，包含 QuestionCard 組件

#### 📋 任務清單

**1. 建立 CAT 問卷資料** [1h]

**檔案**: `frontend/liff/src/data/cat-questions.ts`

**實現步驟**：
1. 從 cat_form.html 提取問題文字
2. 定義 8 題問題 + 6 選項/題
3. 添加 emoji 視覺提示
4. 添加白話文描述

**參考**: ADR-012 § 5.3.4 CAT 問卷資料結構

---

**2. 實現 QuestionCard 組件** [5h]

**檔案**: `frontend/liff/src/components/survey/QuestionCard.tsx`

**實現步驟**：
1. 設計 Layout (Question Text + TTS Button + Options)
2. 實現答案選項按鈕 (6 個 + emoji)
3. 實現 TTS 朗讀按鈕
4. 實現選中狀態視覺反饋
5. 無障礙設計 (aria-label, focus outline)
6. 響應式設計 (Mobile 優先)

**參考**: ADR-012 § 5.3.3.C QuestionCard

**UI 檢查清單**：
- [ ] 問題文字大字體 (20px+)
- [ ] TTS 按鈕明顯可見
- [ ] 選項按鈕大間距 (padding: 16px)
- [ ] 選中狀態清晰 (藍色 border + 勾選 icon)
- [ ] Hover/Active 狀態反饋明確

---

**3. 實現 SurveyHeader 組件** [2h]

**檔案**: `frontend/liff/src/components/survey/SurveyHeader.tsx`

**實現步驟**：
1. 顯示問卷標題
2. 顯示進度條 (當前題號 / 總題數)
3. 顯示 TTS 總開關按鈕
4. 響應式設計

**UI 範例**：
```
┌─────────────────────────────────────┐
│  CAT 健康問卷          🔊           │
├─────────────────────────────────────┤
│  ████████░░░░░░░░ 第 3 題 / 共 8 題 │
└─────────────────────────────────────┘
```

---

### 📅 Day 3 (8h): mMRC + 結果顯示

#### 🎯 目標
實現 mMRC 問卷與 SurveyResult 結果頁

#### 📋 任務清單

**1. 實現 mMRC 問卷** [3h]

**實現步驟**：
1. 建立 mMRC 問卷資料 (1 題, 5 選項)
2. 修改 SurveyPage 支持 CAT/mMRC 切換
3. 實現 mMRC QuestionCard
4. 計算 mMRC Grade (0-4)

**mMRC 選項**：
```typescript
const mmrcOptions = [
  { grade: 0, label: "只有在劇烈運動時才會喘", emoji: "😊" },
  { grade: 1, label: "在平地快走或爬緩坡時會喘", emoji: "🙂" },
  { grade: 2, label: "因為喘的關係，走路比同齡的人慢", emoji: "😐" },
  { grade: 3, label: "在平地走 100 公尺就需要停下來喘氣", emoji: "🙁" },
  { grade: 4, label: "喘到無法離開房間或穿脫衣服時會喘", emoji: "😰" },
];
```

---

**2. 實現 SurveyResult 組件** [3h]

**檔案**: `frontend/liff/src/components/survey/SurveyResult.tsx`

**實現步驟**：
1. 顯示總分數 (CAT: 0-40, mMRC: 0-4)
2. 顯示嚴重度評級 (MILD/MODERATE/SEVERE/VERY_SEVERE)
3. 顯示健康建議文字
4. 實現「完成」按鈕 (關閉 LIFF 或返回首頁)

**UI 範例**：
```
┌─────────────────────────────────────┐
│  🎉 問卷完成！                       │
├─────────────────────────────────────┤
│  您的 CAT 分數: 15 分                │
│  健康狀況: 🟡 中度                   │
│                                      │
│  建議：                              │
│  - 持續記錄每日健康狀況              │
│  - 規律服藥與運動                    │
│  - 如有不適請聯繫治療師              │
│                                      │
│  [ 完成 ]                            │
└─────────────────────────────────────┘
```

---

**3. 整合結果提交 API** [2h]

**實現步驟**：
1. 實現 useSubmitSurvey Hook (TanStack Query Mutation)
2. 調用 POST /surveys/cat 或 POST /surveys/mmrc
3. 處理提交成功/失敗狀態
4. 成功後顯示 SurveyResult

```typescript
// useSubmitSurvey.ts
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useSubmitSurvey() {
  return useMutation({
    mutationFn: async (data: {
      surveyType: 'CAT' | 'mMRC';
      answers: Array<{ question_id: number; answer: number }>;
      total_score: number;
    }) => {
      const endpoint = data.surveyType === 'CAT'
        ? '/surveys/cat'
        : '/surveys/mmrc';

      const response = await apiClient.post(endpoint, data);
      return response.data;
    },
    onSuccess: () => {
      console.log('問卷提交成功');
    },
    onError: (error) => {
      console.error('問卷提交失敗', error);
    },
  });
}
```

---

### 📅 Day 4 (8h): 表單驗證 + TTS 整合測試

#### 🎯 目標
完善表單驗證邏輯，測試 TTS 功能

#### 📋 任務清單

**1. 表單驗證與錯誤處理** [3h]

**實現步驟**：
1. 確保所有問題都已回答才能提交
2. 實現「上一題」按鈕 (可修改已回答的題目)
3. 實現確認對話框 (提交前確認)
4. 網路錯誤處理 (顯示錯誤訊息 + 重試)
5. 提交中 Loading 狀態

**驗證規則**：
- [ ] 所有問題必須回答
- [ ] 分數計算正確 (CAT: sum, mMRC: grade)
- [ ] 提交前確認
- [ ] 網路失敗可重試

---

**2. TTS 整合測試** [3h] ⭐ ADR-011

**測試項目**：
- [ ] 進入問題時自動朗讀 (可選)
- [ ] 點擊 TTS 按鈕正常朗讀
- [ ] 朗讀中顯示正確狀態 (VolumeX icon)
- [ ] 切換問題時停止上一題朗讀
- [ ] iOS Safari 手勢觸發正常
- [ ] Android Chrome 語音正常
- [ ] 語速適合老年人 (0.9x)

**測試裝置**：
- iOS 14+ (Safari / LINE 內建瀏覽器)
- Android 10+ (Chrome)

---

**3. 無障礙性檢查** [2h]

**檢查項目** (WCAG 2.1 AA)：
- [ ] 所有按鈕有 aria-label
- [ ] 表單元素有 label
- [ ] 鍵盤導航正常 (Tab 順序)
- [ ] 焦點可見 (focus outline)
- [ ] 顏色對比度 ≥ 4.5:1
- [ ] 字體大小 ≥ 18px
- [ ] 觸控目標 ≥ 44x44px

**工具**：
- Lighthouse Accessibility
- axe DevTools
- 鍵盤操作測試

---

### 📅 Day 5 (8h): TTS 完整整合 + 可選功能

#### 🎯 目標
完成 Task 5.6 TTS 完整整合，(可選) 開發趨勢圖表元件

#### 📋 任務清單

**1. Task 5.6 - CAT TTS 完整整合** [4h]

**實現步驟**：
1. 實現 TTS 設定頁 (語速調整、開關)
2. 實現自動朗讀設定 (進入問題時)
3. 實現朗讀完成提示
4. 實現多瀏覽器兼容性測試
5. 性能優化 (語音預載入)

**UI 增強**：
- [ ] 設定頁: 自動朗讀開關、語速調整
- [ ] 朗讀進度視覺反饋 (波形動畫)
- [ ] 朗讀完成音效提示 (可選)

---

**2. (可選) Task 5.4 - 趨勢圖表元件** [8h]

**僅在 Day 1-4 提前完成時執行**

**實現步驟**：
1. 抽象 DailyLogsTrendChart 為通用 TrendChart 組件
2. 支持多種圖表類型 (Line, Bar, Area)
3. 支持自定義配色
4. 響應式設計
5. 組件文檔與範例

---

**3. Sprint 3 總結與文檔** [4h]

**實現步驟**：
1. 更新 CHANGELOG_20251022.md
2. 更新 WBS v3.3.1 進度
3. 創建 Sprint 3 演示影片
4. 撰寫交付文檔

---

### ✅ Week 6 驗收標準

**功能驗收**：
- [ ] CAT 8 題問卷正確顯示與提交
- [ ] mMRC 1 題問卷正確顯示與提交
- [ ] TTS 朗讀功能正常 (iOS + Android)
- [ ] 問卷結果正確顯示 (分數 + 嚴重度)
- [ ] 無障礙設計符合 WCAG 2.1 AA
- [ ] 響應式設計 (Mobile 優先)

**技術驗收**：
- [ ] useTTS Hook 正確封裝
- [ ] React Hook Form + Zod 驗證
- [ ] API 提交成功
- [ ] TypeScript 無錯誤
- [ ] Lighthouse Accessibility ≥ 90
- [ ] LCP < 2.0s (LIFF 環境)

---

## 📊 Sprint 3 完成標準 (DoD)

### MUST (必須完成)

- [ ] Task 5.1 - 個案 360° 頁面 ✅ (32h)
  - [ ] PatientDetailPage 正確顯示病患資料
  - [ ] 日誌趨勢圖表正常
  - [ ] 問卷結果顯示正常
  - [ ] Tab 切換功能正常

- [ ] Task 5.2 - Survey API ✅ (24h) **已完成**

- [ ] Task 5.3 - LIFF 問卷頁 ✅ (24h)
  - [ ] CAT 8 題問卷正確
  - [ ] mMRC 1 題問卷正確
  - [ ] 提交成功
  - [ ] 結果顯示正確

- [ ] Task 5.6 - CAT TTS ✅ (8h)
  - [ ] useTTS Hook 實現
  - [ ] TTS 朗讀功能正常
  - [ ] iOS/Android 測試通過

### SHOULD (最好完成)

- [ ] Task 5.4 - 趨勢圖表元件 (16h)
  - 如 Week 6 時間充裕才執行

### DEFERRED (明確延後)

- ~~Task 5.5 - 營養評估 KPI~~ → Sprint 6+ (ADR-010)

---

## 🔧 技術準備清單

### 開發環境

- [ ] Node.js 18+ 已安裝
- [ ] npm / pnpm 最新版
- [ ] VS Code + ESLint + Prettier 已配置
- [ ] Git 配置正確

### 套件安裝

**Dashboard (Next.js)**:
```bash
cd frontend/dashboard

# 核心依賴
npm install @tanstack/react-query
npm install react-hook-form zod @hookform/resolvers/zod
npm install recharts
npm install axios
npm install date-fns
npm install lucide-react

# shadcn/ui 組件 (按需安裝)
npx shadcn-ui@latest add button
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add alert

# Dev 依賴
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

**LIFF (Vite + React)**:
```bash
cd frontend/liff

# 核心依賴
npm install @tanstack/react-query
npm install react-hook-form zod @hookform/resolvers/zod
npm install axios
npm install @line/liff
npm install lucide-react

# shadcn/ui 組件
npx shadcn-ui@latest add button
npx shadcn-ui@latest add progress

# Dev 依賴
npm install -D vitest @testing-library/react
```

### 後端 API 確認

- [ ] `GET /patients/{id}` 可用
- [ ] `GET /daily-logs/patient/{id}` 可用
- [ ] `GET /surveys/patient/{id}` 可用
- [ ] `POST /surveys/cat` 可用
- [ ] `POST /surveys/mmrc` 可用
- [ ] CORS 已正確配置
- [ ] JWT Token 驗證正常

---

## 📈 進度追蹤

### Week 5 進度

| Day | 任務 | 工時 | 狀態 | 完成日期 |
|-----|------|------|------|----------|
| 1-2 | 基礎架構 + API 整合 (Task 5.1.1) | 16h | ✅ | 2025-10-23 |
| 2-3 | 核心組件實現 (Task 5.1.2) | 8h | ✅ | 2025-10-23 |
| 3 | 資料視覺化組件 (Task 5.1.3) | 8h | ⏭️ (跳過 - P2) | - |
| 4 | 錯誤處理 + 測試 (Task 5.1.4) | 8h | ✅ | 2025-10-23 |

### Week 6 進度

| Day | 任務 | 工時 | 狀態 | 完成日期 |
|-----|------|------|------|----------|
| 1 | LIFF 基礎 + useTTS | 8h | ⬜ | - |
| 2 | CAT 問卷 UI | 8h | ⬜ | - |
| 3 | mMRC + 結果顯示 | 8h | ⬜ | - |
| 4 | 驗證 + TTS 測試 | 8h | ⬜ | - |
| 5 | TTS 完整整合 + 可選 | 8h | ⬜ | - |

---

## 🚨 風險管理

### 技術風險

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|----------|
| TTS 瀏覽器兼容性問題 | 中 | 高 | 提前在實機測試 iOS/Android |
| API 回應時間過慢 | 低 | 中 | 實現 Loading 骨架屏 |
| 圖表組件性能問題 | 低 | 中 | 使用 React.memo + 數據限制 |
| LIFF SDK 初始化失敗 | 低 | 高 | 實現降級方案 (Web 版本) |

### 時程風險

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|----------|
| Task 5.1 超時 | 中 | 中 | 優先完成 P0 功能，圖表可簡化 |
| TTS 整合複雜度高於預期 | 低 | 低 | 參考 cat_form.html 實現 |
| 測試時間不足 | 中 | 中 | 優先手動測試核心流程 |

---

## 📚 參考資料

### 內部文檔
- [ADR-010: Sprint 3 MVP 範圍縮減決策](../adr/ADR-010-sprint3-mvp-scope-reduction.md)
- [ADR-011: CAT 無障礙 TTS 技術方案](../adr/ADR-011-cat-accessibility-tts-solution.md)
- [ADR-012: Sprint 3 前端架構設計](../adr/ADR-012-frontend-architecture-sprint3.md)
- [WBS v3.3.1](../16_wbs_development_plan.md)
- [cat_form.html 參考實現](../frontend/cat_form.html)

### 技術文檔
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [React Hook Form Docs](https://react-hook-form.com/)
- [Recharts Docs](https://recharts.org/)
- [Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**制定者**: TaskMaster Hub / Claude Code AI
**審核者**: Technical Lead, Frontend Lead
**最後更新**: 2025-10-22 23:45
**下次檢討**: Week 5 結束 (2025-10-29)

---

**注意事項**：
1. 每日開發前檢查 Todo List
2. 每日結束前更新進度
3. 遇到問題及時記錄與溝通
4. 嚴格遵循驗收標準
5. 優先完成 P0 任務
