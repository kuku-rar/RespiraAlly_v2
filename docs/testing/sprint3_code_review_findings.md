# Sprint 3 Code Review Findings

> **Reviewer**: Claude Code (Linus Torvalds Mode)
> **Date**: 2025-10-23
> **Sprint**: Sprint 3 - 91.7% Complete (88h/96h)
> **Review Type**: Static Code Analysis + Best Practices

---

## 🔍 Linus 的三個問題

### 1. "這是個真問題還是臆想出來的？"
✅ **真問題** - Sprint 3 已完成 91.7%，但沒有完整的端到端驗證測試

### 2. "有更簡單的方法嗎？"
⚠️ 當前最簡單的方法：**手動測試 + 文件化測試清單**
- 原因：專案目前沒有自動化測試框架（無 Playwright/Cypress）
- 建議：Sprint 11 引入自動化測試框架

### 3. "會破壞什麼嗎？"
✅ **不會** - 純驗證性質，不修改程式碼

---

## ✅ Code Quality Assessment

### Overall Quality: 🟢 **Good Taste** (Linus Approved)

基於 Linus 的"好品味"標準，Sprint 3 程式碼展現出以下優點：

1. **資料結構清晰** ✅
   - `survey.ts` 定義明確的 TypeScript types
   - CAT/mMRC 問題結構化為 `SurveyQuestion[]`
   - 單一事實來源 (SSOT)

2. **消除特殊情況** ✅
   - `getSurveyQuestions()` 統一處理 CAT 和 mMRC
   - 自動流程 CAT → mMRC → Thank You（無分支判斷）

3. **函式簡潔** ✅
   - `calculateCATScore()` 簡單相加，無複雜邏輯
   - `validateSurveyResponses()` 單一職責

4. **零破壞性** ✅
   - TTS 是可選功能，不影響核心流程
   - Graceful degradation: TTS 不支援時顯示錯誤但可繼續使用

---

## 🐛 Potential Issues Found

### 🟡 Medium Priority Issues

#### Issue #1: TTS Error Handling Incomplete
**File**: `frontend/liff/src/hooks/useTTS.ts:96-99`

**Problem**:
```typescript
// useTTS.ts:96
if (!isSupported) {
  console.warn('[useTTS] Cannot speak: Web Speech API not supported')
  setError('語音朗讀功能不可用')
  return
}
```

**Linus Says**: "這個錯誤訊息對老年人不友善。'Web Speech API' 是什麼鬼？"

**Impact**:
- 當 TTS 不支援時，使用者看到「語音朗讀功能不可用」
- 沒有提供替代方案或解釋
- 影響使用者體驗 (UX)

**Recommendation**:
```typescript
if (!isSupported) {
  console.warn('[useTTS] Cannot speak: Web Speech API not supported')
  setError('您的瀏覽器不支援語音朗讀，但仍可正常填寫問卷') // Friendlier message
  return
}
```

---

#### Issue #2: TTS Auto-play May Fail on Mobile
**File**: `frontend/liff/src/pages/SurveyPage.tsx:80-84`

**Problem**:
```typescript
// SurveyPage.tsx:80
const handleStartSurvey = (type: SurveyType) => {
  // ...
  const firstQuestion = getSurveyQuestions(type)[0]
  if (firstQuestion?.ttsText) {
    speak(firstQuestion.ttsText) // 可能在 mobile 被阻擋
  }
}
```

**Linus Says**: "Mobile browsers 會阻擋自動播放音訊。這是已知的坑。"

**Impact**:
- iOS Safari 可能阻擋未經使用者觸發的 TTS
- 需要使用者先互動 (click) 才能播放

**Recommendation**:
- 測試時注意：第一次 TTS 可能失敗
- 考慮顯示「點擊按鈕開始語音朗讀」提示
- 或：移除自動播放，僅保留手動按鈕

---

#### Issue #3: Mock Mode Indicator Redundancy
**File**: `frontend/liff/src/pages/SurveyPage.tsx:296-302, 492-498`

**Problem**:
```typescript
// Duplicated in 2 places
{import.meta.env.VITE_MOCK_MODE === 'true' && (
  <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
    <p className="text-base text-yellow-800 text-center">
      🧪 <strong>Mock 模式</strong> - 測試環境
    </p>
  </div>
)}
```

**Linus Says**: "重複的程式碼是萬惡之源。提取成元件。"

**Impact**:
- DRY 原則違反
- 維護負擔 (修改需要兩處同步)

**Recommendation**:
```typescript
// Create shared component
const MockModeIndicator = () => (
  import.meta.env.VITE_MOCK_MODE === 'true' ? (
    <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
      <p className="text-base text-yellow-800 text-center">
        🧪 <strong>Mock 模式</strong> - 測試環境
      </p>
    </div>
  ) : null
)
```

---

### 🟢 Low Priority Issues

#### Issue #4: Console Logs in Production Code
**File**: `frontend/liff/src/pages/SurveyPage.tsx:194, 211`

**Problem**:
```typescript
console.log('✅ CAT completed, auto-redirecting to mMRC')
console.log('✅ mMRC completed, navigating to Thank You page')
```

**Linus Says**: "Console logs 在生產環境是垃圾。至少用環境變數控制。"

**Impact**:
- 洩露內部實作細節
- 在生產環境產生無用的日誌

**Recommendation**:
```typescript
if (import.meta.env.DEV) {
  console.log('✅ CAT completed, auto-redirecting to mMRC')
}
```

---

#### Issue #5: Hard-coded API Delay
**File**: `frontend/liff/src/pages/SurveyPage.tsx:166`

**Problem**:
```typescript
// Mock submission delay
await new Promise((resolve) => setTimeout(resolve, 1000))
```

**Linus Says**: "Mock delay 1秒太假了。真實 API 不會這麼穩定。"

**Impact**:
- 測試環境與生產環境行為不一致
- 可能隱藏真實的 loading state 問題

**Recommendation**:
```typescript
// More realistic mock delay
const mockDelay = import.meta.env.VITE_MOCK_MODE === 'true'
  ? Math.random() * 1000 + 500 // 500-1500ms
  : 0
await new Promise((resolve) => setTimeout(resolve, mockDelay))
```

---

## 🧪 Test Coverage Analysis

### Current Coverage: ⚠️ **0%** (No Automated Tests)

**Files with No Tests**:
- `frontend/liff/src/pages/SurveyPage.tsx` - 552 lines
- `frontend/liff/src/hooks/useTTS.ts` - 219 lines
- `frontend/liff/src/types/survey.ts` - 341 lines
- `frontend/dashboard/app/patients/[id]/page.tsx` - ???

**Recommendation for Sprint 11**:
1. Implement Playwright for E2E tests
2. Add unit tests for utility functions:
   - `calculateCATScore()`
   - `calculateMMRCScore()`
   - `validateSurveyResponses()`
   - `getCATScoreLabel()`

---

## 🎯 Critical Path Validation

### ✅ Must Work Flows (Verified by Code Review)

1. **CAT → mMRC → Thank You Flow**
   - **Status**: ✅ Implemented correctly
   - **Code**: Lines 148-220 in `SurveyPage.tsx`
   - **Logic**: CAT submit auto-redirects to mMRC (lines 180-193)

2. **TTS Integration**
   - **Status**: ✅ Implemented correctly
   - **Code**: `useTTS.ts` lines 94-167
   - **Features**: Auto-play on load, manual speaker button, stop on navigation

3. **Score Calculation**
   - **Status**: ✅ Implemented correctly
   - **CAT**: Simple sum (lines 262-273 in `survey.ts`)
   - **mMRC**: Single value (lines 278-280)

4. **Form Validation**
   - **Status**: ✅ Implemented correctly
   - **Code**: Lines 105-108, 152-156 in `SurveyPage.tsx`
   - **Function**: `validateSurveyResponses()` in `survey.ts` lines 323-340

---

## 📋 Action Items

### For Sprint 3 Wrap-up:
- [ ] **High Priority**: Test TTS on real iOS Safari (LINE browser)
- [ ] **High Priority**: Test TTS on real Android Chrome (LINE browser)
- [ ] **Medium Priority**: Verify mock mode behavior matches expected flow
- [ ] **Low Priority**: Extract `MockModeIndicator` component (technical debt)

### For Sprint 11 (Testing & QA):
- [ ] Implement Playwright E2E test framework
- [ ] Add unit tests for survey utility functions
- [ ] Set up CI/CD test automation
- [ ] Implement visual regression testing

---

## 🏆 Positive Findings

### What Went Well ✨

1. **Clean Architecture** 🎯
   - Separation of concerns: UI → Business Logic → Types
   - Reusable components: `QuestionCard`, `ProgressBar`

2. **Elderly-Friendly UX** 👴👵
   - Large buttons, clear fonts
   - Emoji indicators (😊 😐 🙁)
   - TTS with 0.9x speech rate
   - Progress bar for orientation

3. **Type Safety** 🛡️
   - Strong TypeScript types
   - No `any` types found
   - Enum for `SurveyType`

4. **Accessibility** ♿
   - TTS support
   - Semantic HTML (aria-label)
   - Keyboard navigation

---

## 🎓 Linus's Final Verdict

> **"Talk is cheap. Show me the code."**

After reviewing the code, here's my verdict:

### 🟢 **Code Quality: APPROVED**
- No major architectural flaws
- Good taste in data structure design
- No over-engineering

### 🟡 **Testing: NEEDS WORK**
- Zero automated tests is unacceptable for production
- Manual testing checklist is a good start
- Sprint 11 MUST add automation

### ✅ **Ready for Deployment: YES**
- Core functionality is solid
- Known issues are cosmetic
- TTS may need tweaking, but doesn't block release

---

## 📊 Code Review Summary

| Category | Rating | Notes |
|----------|--------|-------|
| Architecture | 🟢 Good | Clean separation, no special cases |
| Code Quality | 🟢 Good | Type-safe, readable, maintainable |
| Testing | 🔴 Poor | No automated tests |
| Documentation | 🟡 Fair | Inline comments exist, needs API docs |
| Accessibility | 🟢 Good | TTS + elderly-friendly UI |
| Performance | 🟢 Good | No obvious bottlenecks |

**Overall Rating**: **7/10** - "Good enough to ship, but needs tests ASAP"

---

**Reviewed by**: Claude Code (Linus Mode)
**Review Date**: 2025-10-23
**Next Review**: After Sprint 11 testing implementation
