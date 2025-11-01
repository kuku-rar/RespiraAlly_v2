# Testing Directory - 測試資料與腳本

本目錄包含 RespiraAlly V2.0 的所有測試腳本、測試資料和測試結果。

## 📁 目錄結構

```
testing/
├── README.md                           # 本檔案
├── test_auth_api.py                    # Authentication API 測試腳本
├── test_patient_api_fixed.py           # Patient Management API 測試腳本
├── test_task_fixed.py                  # Task Board API 測試腳本
├── auth_api_test_results.json          # Authentication API 測試結果
├── patient_api_results_fixed.json      # Patient Management API 測試結果
├── task_api_results.json               # Task Board API 測試結果
└── [歷史測試記錄]                       # 過往 Sprint 的測試文件
```

## 🧪 測試腳本說明

### 1. Authentication API 測試 (`test_auth_api.py`)

**測試範圍**:
- ✅ 治療師登入（有效/無效憑證）
- ✅ 治療師註冊（成功/重複郵箱）
- ✅ Token 刷新 (Refresh Token)
- ✅ 登出 (Logout)
- ✅ Token 驗證（有效/無效/已撤銷）
- ✅ 受保護端點訪問控制

**執行方式**:
```bash
cd /mnt/a/AIPE01_期末專題/RespiraAlly/docs/testing
python3 test_auth_api.py
```

**測試結果**: `auth_api_test_results.json`

**通過率**: 91.7% (11/12)

---

### 2. Patient Management API 測試 (`test_patient_api_fixed.py`)

**測試範圍**:
- ✅ 建立病患 (Create Patient)
- ✅ 取得病患詳情 (Get Patient)
- ✅ 更新病患資訊 (Update Patient)
- ✅ 列出病患（分頁、搜尋、過濾）
- ✅ 授權檢查（Therapist only）
- ✅ 錯誤處理（404, 401, 422）

**執行方式**:
```bash
python3 test_patient_api_fixed.py
```

**測試結果**: `patient_api_results_fixed.json`

**通過率**: 87.5% (7/8)

---

### 3. Task Board API 測試 (`test_task_fixed.py`)

**測試範圍**:
- ⚠️ 建立任務 (Create Task) - **受後端 bug 阻塞**
- ⚠️ 任務狀態轉換 (Start/Complete/Cancel) - **受阻**
- ✅ 列出病患任務
- ⚠️ 列出治療師任務 - **受阻**
- ⚠️ 任務統計 - **受阻**

**執行方式**:
```bash
python3 test_task_fixed.py
```

**測試結果**: `task_api_results.json` (部分結果)

**通過率**: 16.7% (1/6) - **因後端 P0 bug 阻塞**

**已知問題**:
- 🚨 P0: `TokenData.sub` 屬性錯誤 → 應使用 `user_id`
- 🚨 P0: `TaskRepositoryImpl.get_overdue_tasks()` 方法簽名錯誤

---

## 📊 測試結果檔案

所有測試結果以 JSON 格式儲存，包含以下資訊：
- 測試名稱 (test_name)
- 測試端點 (endpoint)
- HTTP 方法 (method)
- 成功與否 (success)
- HTTP 狀態碼 (status_code)
- 測試備註 (notes)
- 時間戳記 (timestamp)

### 查看測試結果範例：
```bash
# 查看 Authentication 測試結果
cat auth_api_test_results.json | python3 -m json.tool

# 統計通過率
cat auth_api_test_results.json | python3 -c "import json, sys; data=json.load(sys.stdin); passed=sum(1 for r in data if r['success']); print(f'通過率: {passed}/{len(data)} ({passed/len(data)*100:.1f}%)')"
```

---

## 🔄 重新執行測試

### 前置條件
1. 後端服務運行於 `http://localhost:8000`
2. 資料庫已初始化並有測試數據
3. Python 3.10+ 環境
4. 安裝 `requests` 套件: `pip install requests`

### 執行所有測試
```bash
# 依序執行所有測試
python3 test_auth_api.py
python3 test_patient_api_fixed.py
python3 test_task_fixed.py  # 注意：需修復後端 bug 後才能完整測試
```

### 修復後端 Bug 後重新測試
```bash
# 修復以下問題：
# 1. 全域替換 current_user.sub → current_user.user_id
# 2. 修正 TaskRepositoryImpl.get_overdue_tasks() 方法簽名
# 3. 檢查 Token blacklist Redis 連接

# 然後重新執行
python3 test_task_fixed.py
```

---

## 📈 測試覆蓋率

### 已測試的 Bounded Contexts
- ✅ **Authentication** - 100% 端點覆蓋
- ✅ **Patient Management** - 100% 核心端點覆蓋
- ⚠️ **Task Board** - 約 20% 覆蓋（受後端 bug 阻塞）

### 待測試的 Bounded Contexts
- ⏭️ Daily Log Management
- ⏭️ Risk Assessment
- ⏭️ Alert System (Sprint 4)
- ⏭️ RAG Chatbot
- ⏭️ Survey Management
- ⏭️ Notification System

---

## 🐛 已知問題與修復狀態

| Bug ID | 嚴重度 | 描述 | 狀態 | 修復預估 |
|--------|--------|------|------|----------|
| #1 | P0 | Task API TokenData.sub 錯誤 | 🔴 待修復 | 30 分鐘 |
| #2 | P0 | TaskRepositoryImpl 方法簽名錯誤 | 🔴 待修復 | 15 分鐘 |
| #3 | P1 | Token Blacklist 功能失效 | 🔴 待修復 | 1-2 小時 |

---

## 📝 測試標準參考

本測試套件遵循以下標準：
- [API Development Checklist](/mnt/a/AIPE01_期末專題/RespiraAlly/docs/project_management/templates/api_development_checklist_template.md)
- [Feature Alignment Verification](/mnt/a/AIPE01_期末專題/RespiraAlly/docs/project_management/templates/feature_alignment_verification_template.md)
- [Code Review Guide](/mnt/a/AIPE01_期末專題/RespiraAlly/docs/11_code_review_and_refactoring_guide.md)

---

## 📊 完整測試報告

完整的測試報告請參考：
- **最新報告**: `/mnt/a/AIPE01_期末專題/RespiraAlly/docs/test_reports/test_report_20251030.md`
- **報告目錄**: `/mnt/a/AIPE01_期末專題/RespiraAlly/docs/test_reports/`

---

## 🚀 後續測試計畫

### 短期 (本週)
1. ✅ 修復 P0 bugs (Bug #1, #2)
2. ✅ 重新執行 Task Board 完整測試
3. ✅ 達到 Task Board 90% 測試覆蓋率

### 中期 (本月)
4. ⏭️ 完成 Daily Log API 測試
5. ⏭️ 完成 Risk Assessment API 測試
6. ⏭️ 完成 Alert System API 測試
7. ⏭️ 達到 7 個 Bounded Contexts 80% 覆蓋率

### 長期 (下個月)
8. ⏭️ 端到端 (E2E) 測試：完整使用者流程
9. ⏭️ 效能測試：壓力測試與負載測試
10. ⏭️ 自動化 CI/CD 測試 pipeline

---

**最後更新**: 2025-10-30
**維護者**: RespiraAlly Development Team
**問題回報**: 請在 GitHub Issues 提出測試相關問題
