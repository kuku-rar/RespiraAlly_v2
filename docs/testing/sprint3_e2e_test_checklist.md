# Sprint 3 E2E Testing Checklist

> **Version**: 1.0
> **Date**: 2025-10-23
> **Sprint**: Sprint 3 收尾與驗證
> **Testing Type**: Manual End-to-End Testing
> **Tester**: Claude Code + Human Verification
> **Status**: 🟡 In Progress

---

## 📋 Testing Overview

### Scope
Sprint 3 delivered the following features:
- ✅ **Task 5.1**: Patient 360° Dashboard Page
- ✅ **Task 5.2**: CAT & mMRC Survey Backend API
- ✅ **Task 5.3**: LIFF Survey Forms (CAT 8 questions + mMRC 1 question)
- ✅ **Task 5.6**: TTS Accessibility (Elderly-friendly voice support)
- ✅ **Form Corrections**: Registration & Daily Log form fixes per user feedback

### Testing Goals
1. **Functional Correctness**: All features work as specified
2. **User Experience**: Smooth workflows without friction
3. **Accessibility**: TTS works on target devices (iOS Safari + Android Chrome)
4. **Data Integrity**: Form validation prevents invalid input
5. **Cross-browser Compatibility**: Works on LINE browser environment

---

## 🧪 Test Cases

### 1. Therapist Workflow (Dashboard)

#### 1.1 Login & Authentication
- [ ] **TC-D-001**: Therapist can log in with valid credentials
  - **Steps**:
    1. Navigate to `/login`
    2. Enter therapist credentials
    3. Click "登入" button
  - **Expected**: Redirected to `/dashboard` with patient list
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 1.2 Patient List View
- [ ] **TC-D-002**: Patient list displays correctly
  - **Steps**:
    1. Log in as therapist
    2. View patient list on dashboard
  - **Expected**: Shows patient cards with name, age, risk level, last updated
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 1.3 Patient 360° View (Sprint 3 核心功能)
- [ ] **TC-D-003**: Navigate to patient detail page
  - **Steps**:
    1. Click on any patient card
    2. Verify URL: `/patients/[patient_id]`
  - **Expected**: Patient 360° page loads with header
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-D-004**: Patient Header displays correct information
  - **Steps**:
    1. On patient detail page
    2. Check PatientHeader component
  - **Expected**: Shows patient name, age, contact, therapist info
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-D-005**: Patient Tabs navigation works
  - **Steps**:
    1. On patient detail page
    2. Click through tabs: Daily Logs, Surveys, KPIs
  - **Expected**: Tab content switches correctly
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-D-006**: View patient surveys (CAT & mMRC)
  - **Steps**:
    1. Navigate to "Surveys" tab
    2. Check CAT survey results
    3. Check mMRC survey results
  - **Expected**:
    - CAT score displayed (0-40)
    - mMRC grade displayed (Grade 0-4)
    - Score labels shown correctly
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-D-007**: View daily logs (last 7 days)
  - **Steps**:
    1. Navigate to "Daily Logs" tab
    2. Check log entries
  - **Expected**: Shows last 7 days of logs with SpO2, symptoms, exercise
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

---

### 2. Patient Workflow (LIFF)

#### 2.1 LIFF Initialization
- [ ] **TC-L-001**: LIFF app loads in LINE browser
  - **Steps**:
    1. Open LIFF link in LINE app
    2. Wait for LIFF.init()
  - **Expected**: App loads without errors
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip
  - **Devices Tested**:
    - ⬜ iOS Safari (LINE browser)
    - ⬜ Android Chrome (LINE browser)

#### 2.2 Survey Selection
- [ ] **TC-L-002**: Survey selection page displays correctly
  - **Steps**:
    1. Navigate to `/survey` page
    2. Check available surveys
  - **Expected**: Shows 2 options: CAT & mMRC
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 2.3 CAT Survey Flow (8 Questions)
- [ ] **TC-L-003**: Start CAT survey
  - **Steps**:
    1. Click "CAT 評估測試" button
  - **Expected**: First question appears with ProgressBar (1/8)
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-004**: CAT Question 1 - Cough
  - **Steps**:
    1. Read question: "請問您最近咳嗽的情形？"
    2. Check options: 0-5 scale with emojis
    3. Select option (value: 2)
  - **Expected**: Option highlighted, no error
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-005**: CAT Navigation - Next
  - **Steps**:
    1. Select answer for Question 1
    2. Click "下一題 →" button
  - **Expected**: Progress bar updates (2/8), next question shows
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-006**: CAT Navigation - Previous
  - **Steps**:
    1. On Question 2
    2. Click "← 上一題" button
  - **Expected**: Returns to Question 1, previous answer still selected
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-007**: CAT All 8 Questions
  - **Steps**:
    1. Answer all 8 CAT questions:
       - Q1: cough
       - Q2: phlegm
       - Q3: chest_tightness
       - Q4: breathlessness
       - Q5: activity_limitation
       - Q6: confidence
       - Q7: sleep
       - Q8: energy
  - **Expected**: Each question displays with 0-5 options
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-008**: CAT Submit
  - **Steps**:
    1. On Question 8, click "提交問卷 →"
  - **Expected**: Auto-redirects to mMRC (no result page shown)
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 2.4 mMRC Survey Flow (1 Question) - Auto Flow
- [ ] **TC-L-009**: mMRC auto-starts after CAT
  - **Steps**:
    1. Complete CAT survey
    2. Verify mMRC starts automatically
  - **Expected**:
    - mMRC form appears
    - Progress bar shows (1/1)
    - Question text: "請選擇最符合您呼吸困難程度的描述"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-010**: mMRC Question - Dyspnea Grade
  - **Steps**:
    1. Read question text
    2. Check options: Grade 0-4
    3. Select Grade 2
  - **Expected**: 5 options with descriptions, Grade 2 highlighted
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-011**: mMRC Submit
  - **Steps**:
    1. Select Grade 2
    2. Click "提交問卷 →"
  - **Expected**: Navigates to Thank You page
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 2.5 Thank You Page (Final Results)
- [ ] **TC-L-012**: Thank You page displays CAT + mMRC results
  - **Steps**:
    1. Complete both surveys
    2. Check Thank You page content
  - **Expected**:
    - Success header: "問卷填寫完成！ ✅"
    - **CAT Score Card**:
      - Total score (e.g., 16/40)
      - Score label (e.g., "中度影響")
    - **mMRC Score Card**:
      - Grade (e.g., 2)
      - Description (e.g., "Grade 2 - 走路比同齡慢或需停下來喘氣")
    - Action buttons: "返回首頁", "重新填寫問卷"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-L-013**: Score calculation correctness
  - **Steps**:
    1. Complete CAT with known answers (e.g., all 2s)
    2. Verify CAT score = 2 + 2 + 2 + 2 + 2 + 2 + 2 + 2 = 16
    3. Complete mMRC with Grade 2
    4. Verify mMRC score = 2
  - **Expected**: Scores calculated correctly
  - **Actual**:
    - CAT Score: ___________
    - mMRC Grade: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

---

### 3. TTS Accessibility (Sprint 3 Task 5.6)

#### 3.1 TTS Initialization
- [ ] **TC-T-001**: TTS support detection
  - **Steps**:
    1. Open LIFF survey page
    2. Check browser console for TTS support message
  - **Expected**: Console shows "[useTTS] Web Speech API supported ✅"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip
  - **Devices Tested**:
    - ⬜ iOS Safari 14+ (LINE browser)
    - ⬜ Android Chrome 90+ (LINE browser)
    - ⬜ Desktop Chrome/Edge

#### 3.2 TTS Auto-play on Question Load
- [ ] **TC-T-002**: CAT Question 1 auto-reads with TTS
  - **Steps**:
    1. Start CAT survey
    2. Wait for TTS to start
    3. Listen to audio
  - **Expected**:
    - TTS speaks: "請問您最近咳嗽的情形？請選擇最符合您情況的選項，從 0 到 5"
    - Speech rate: 0.9x (elderly-friendly)
    - Language: zh-TW
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-T-003**: TTS auto-reads on "Next" button
  - **Steps**:
    1. Answer Question 1
    2. Click "下一題 →"
    3. Listen to next question TTS
  - **Expected**: New question reads automatically
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-T-004**: TTS auto-reads on "Previous" button
  - **Steps**:
    1. On Question 2
    2. Click "← 上一題"
    3. Listen to previous question TTS
  - **Expected**: Previous question reads again
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 3.3 TTS Controls
- [ ] **TC-T-005**: QuestionCard TTS speaker button
  - **Steps**:
    1. On any question
    2. Look for speaker button (🔊 icon)
    3. Click speaker button
  - **Expected**: Question text is read aloud
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-T-006**: TTS stop on navigation
  - **Steps**:
    1. Start TTS playback
    2. Before TTS finishes, click "下一題"
  - **Expected**: Current TTS stops, new question TTS starts
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 3.4 TTS Cross-Browser Compatibility
- [ ] **TC-T-007**: iOS Safari (LINE browser) TTS
  - **Device**: iPhone (iOS 14+)
  - **Browser**: LINE built-in browser
  - **Test**:
    1. Open LIFF survey
    2. Complete CAT with TTS
    3. Check audio quality
  - **Expected**: TTS works smoothly, voice is clear
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-T-008**: Android Chrome (LINE browser) TTS
  - **Device**: Android phone (Chrome 90+)
  - **Browser**: LINE built-in browser
  - **Test**:
    1. Open LIFF survey
    2. Complete CAT with TTS
    3. Check audio quality
  - **Expected**: TTS works smoothly, voice is clear
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

---

### 4. Form Validation

#### 4.1 CAT Survey Validation
- [ ] **TC-V-001**: Required question validation
  - **Steps**:
    1. Start CAT survey
    2. On Question 1, do NOT select any option
    3. Click "下一題 →"
  - **Expected**: Error message: "請選擇一個答案"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-V-002**: Submit without all answers
  - **Steps**:
    1. Answer only Questions 1-7
    2. Leave Question 8 blank
    3. Try to submit
  - **Expected**: Error message: "請回答所有必填問題"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 4.2 mMRC Survey Validation
- [ ] **TC-V-003**: mMRC required validation
  - **Steps**:
    1. Complete CAT
    2. On mMRC question, do NOT select
    3. Click "提交問卷 →"
  - **Expected**: Error message shown
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 4.3 Registration Form Validation (Per User Feedback)
- [ ] **TC-V-004**: Registration form field validation
  - **Steps**:
    1. Navigate to `/register`
    2. Test field validations:
       - Height: 100-250 cm
       - Weight: 30-200 kg
       - Smoking years: 0-100
       - Exercise hours: 0-24
  - **Expected**: Invalid inputs rejected with error messages
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 4.4 Daily Log Form Validation (Per User Feedback)
- [ ] **TC-V-005**: Daily log form field validation
  - **Steps**:
    1. Navigate to `/daily-log`
    2. Test field validations:
       - SpO2: 50-100%
       - Temperature: 35.0-42.0°C
       - Heart rate: 40-200 bpm
  - **Expected**: Invalid inputs rejected with error messages
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

---

### 5. Score Calculation Verification

#### 5.1 CAT Score Calculation
Test different CAT answer combinations to verify score calculation logic:

- [ ] **TC-S-001**: CAT Score - All zeros
  - **Answers**: All questions → 0
  - **Expected Score**: 0
  - **Expected Label**: "低影響 (0/40)"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-002**: CAT Score - All ones
  - **Answers**: All questions → 1
  - **Expected Score**: 8
  - **Expected Label**: "低影響 (8/40)"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-003**: CAT Score - Medium impact
  - **Answers**: All questions → 2
  - **Expected Score**: 16
  - **Expected Label**: "中度影響 (16/40)"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-004**: CAT Score - High impact
  - **Answers**: All questions → 3
  - **Expected Score**: 24
  - **Expected Label**: "高度影響 (24/40)"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-005**: CAT Score - Very high impact
  - **Answers**: All questions → 5
  - **Expected Score**: 40
  - **Expected Label**: "極高影響 (40/40)"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

#### 5.2 mMRC Score Calculation
- [ ] **TC-S-006**: mMRC Grade 0
  - **Answer**: dyspnea_grade → 0
  - **Expected**: "Grade 0 - 僅在劇烈運動時喘"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-007**: mMRC Grade 1
  - **Answer**: dyspnea_grade → 1
  - **Expected**: "Grade 1 - 快走或爬緩坡時喘"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-008**: mMRC Grade 2
  - **Answer**: dyspnea_grade → 2
  - **Expected**: "Grade 2 - 走路比同齡慢或需停下來喘氣"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-009**: mMRC Grade 3
  - **Answer**: dyspnea_grade → 3
  - **Expected**: "Grade 3 - 走100公尺或數分鐘就需停下來喘氣"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

- [ ] **TC-S-010**: mMRC Grade 4
  - **Answer**: dyspnea_grade → 4
  - **Expected**: "Grade 4 - 穿衣或脫衣時就會喘"
  - **Actual**: ___________
  - **Status**: ⬜ Pass / ⬜ Fail / ⬜ Skip

---

## 📊 Testing Summary

### Test Execution Statistics
- **Total Test Cases**: 47
- **Passed**: ___________
- **Failed**: ___________
- **Skipped**: ___________
- **Pass Rate**: ___________%

### Critical Issues Found
| Issue ID | Severity | Component | Description | Status |
|----------|----------|-----------|-------------|--------|
| _____ | _____ | _____ | _____ | _____ |

### Known Limitations
- TTS may not work on older browsers (< iOS 14, < Chrome 90)
- LINE browser environment may have specific quirks
- Mock mode is enabled for testing (VITE_MOCK_MODE=true)

---

## ✅ Sign-off

### Tester
- **Name**: Claude Code
- **Date**: ___________
- **Signature**: ___________

### Reviewer
- **Name**: ___________
- **Date**: ___________
- **Signature**: ___________

---

## 📝 Notes
- This is a **manual testing checklist** because no automated E2E framework exists yet
- For Sprint 4+, consider implementing Playwright/Cypress for automation
- TTS testing requires physical devices (iOS + Android)
- All test cases should be re-run after bug fixes

---

**Generated by**: Claude Code - Sprint 3 E2E Testing
**Based on**: `frontend/liff/src/pages/SurveyPage.tsx`, `frontend/dashboard/app/patients/[id]/page.tsx`, ADR-011 TTS Simplification
