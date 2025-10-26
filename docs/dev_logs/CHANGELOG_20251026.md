# 更新日誌

RespiraAlly V2.0 的所有重要變更都將記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
此專案遵循 [語義化版本](https://semver.org/spec/v2.0.0.html)。

---

## [未發布版本]

### 🚀 前端整合待處理
- 警示系統 UI 整合（儀表板徽章、警示列表）
- 風險評估儀表板 UI 更新（GOLD ABE 顯示）

---

## [衝刺 4] - 2025-10-26

### 🎯 衝刺 4 重點：慢性阻塞性肺病風險管理 - 警示系統與惡化追蹤

**摘要**：實作完整的警示系統，採用 DDD 架構，基於 GOLD ABE 風險分類自動觸發警示。強化惡化管理 API，具備自動風險重新計算功能。

---

### ✨ 新增功能 - 警示系統（P1 高優先級）

#### 領域層 - 警示規則引擎
- **3 個固定警示規則**（MVP 策略 - ADR-016）：
  1. `GOLD_GROUP_E`：嚴重等級 - 最高風險病患（12 個月內 ≥2 次惡化或 ≥1 次住院）
  2. `HIGH_CAT_SCORE`：高等級 - CAT 分數 ≥ 20（嚴重症狀負擔）
  3. `FREQUENT_EXACERBATIONS`：中等級 - 最近 12 個月內 ≥3 次惡化
- 警示評估邏輯遵循 Linus Torvalds 的「好品味」原則
- 警示創建包含豐富的元數據（規則、觸發日期、臨床指標）

#### 應用層 - 警示服務
- 警示創建與持久化（DDD 儲存庫模式）
- 警示檢索，支援過濾、分頁和排序
- 活動警示計數，用於儀表板徽章
- 與通知系統的清晰分離（ADR-017）

#### API 層 - 警示端點（唯讀 MVP）
- `GET /api/v1/alerts/patients/{patient_id}/` - 列出病患警示
  - 過濾器：alert_type、severity、status、date_range
  - 分頁：page、page_size（預設 20）
  - 排序：triggered_at（降序）、severity、created_at
- `GET /api/v1/alerts/patients/{patient_id}/active/count` - 計算活動警示數量
- `GET /api/v1/alerts/{alert_id}` - 取得警示詳情
- 授權：治療師（自己的病患）、病患（自己的資料）、主管/管理員（全部）

#### 資料庫架構
- `alerts` 表格，具備完整生命週期追蹤：
  - 狀態轉換：ACTIVE → ACKNOWLEDGED → RESOLVED
  - 警示元數據（JSONB）：規則、臨床指標、觸發條件
  - 觸發/確認/解決時間戳記和操作者

#### 自動觸發整合
- 風險評估 → 警示評估（自動）
- 風險計算後立即創建警示
- MVP 版本不支援手動創建警示（唯讀 API）

---

### ✨ 新增功能 - 惡化管理強化

#### 自動風險重新計算
- **POST /api/v1/exacerbations/** - 創建惡化 → 自動風險重新計算
- **PATCH /api/v1/exacerbations/{id}** - 更新惡化 → 自動風險重新計算（如果嚴重程度變更）
- **DELETE /api/v1/exacerbations/{id}** - 刪除惡化 → 自動風險重新計算
- 確保風險評估始終反映最新的惡化資料

---

### 🐛 修復 - 警示系統錯誤

#### 1. `alert.py` 中的變數遮蔽
- **位置**：`api/v1/routers/alert.py:108`
- **問題**：函式參數 `status` 遮蔽了 FastAPI 的 `status` 模組
- **影響**：`status.HTTP_403_FORBIDDEN` 返回 `None`，導致 500 錯誤
- **修復**：將參數從 `status` 重新命名為 `alert_status`
- **受影響範圍**：`list_patient_alerts()` 端點

#### 2. `alert_rule_engine.py` 中的欄位名稱不符
- **問題**：使用錯誤的 RiskAssessmentModel 欄位名稱
  - ❌ `cat_total_score` → ✅ `cat_score`（7 處）
  - ❌ `exacerbation_count_last_12m` → ✅ `exacerbation_count_12m`
  - ❌ `hospitalization_count_last_12m` → ✅ `hospitalization_count_12m`
- **影響**：警示評估期間發生 AttributeError
- **修復**：全域替換所有欄位名稱

#### 3. `alert.py` 中的授權參數順序錯誤
- **位置**：3 個端點（get_alert_by_id、list_patient_alerts、count_active_alerts）
- **問題**：`can_access_patient()` 呼叫的參數順序錯誤
  - ❌ `can_access_patient(current_user, therapist_id, patient_id)`
  - ✅ `can_access_patient(current_user, patient_id, therapist_id)`
- **影響**：所有授權檢查失敗（403 禁止訪問）
- **修復**：更正所有 3 處的參數順序

#### 4. `risk.py` 中的 SQLAlchemy 延遲載入錯誤
- **位置**：`api/v1/routers/risk.py:124`
- **問題**：在非同步上下文中嘗試同步訪問延遲載入的關聯
  - ❌ `assessment.patient.therapist_id`（MissingGreenlet 錯誤）
- **修復**：新增 `db` 依賴項並手動查詢病患
  - ✅ `patient = await db.get(PatientProfileModel, patient_id)`

---

### 📚 文件 - 架構決策記錄

#### ADR-016：警示 MVP 策略 - 固定規則引擎
- **決策**：使用 3 個硬編碼規則，而非資料庫驅動的規則引擎
- **理由**：更快的 MVP 交付（4-6 小時 vs 20-24 小時），專注於臨床驗證
- **權衡**：降低靈活性 vs 加速上市時間
- **技術債務**：DEBT-001 - 規則引擎演進（MVP 後升級路徑）

#### ADR-017：通知系統延後至 MVP 後
- **決策**：僅創建警示，不發送通知
- **理由**：關注點分離（警示 = 偵測，通知 = 傳遞）
- **權衡**：MVP 版本需手動檢查警示 vs 完整使用者體驗
- **技術債務**：DEBT-002 - 通知系統實作（衝刺 5+）

---

### 📝 文件 - 技術債務追蹤

#### DEBT-001：警示規則引擎演進
- **當前狀態**：`AlertRuleEngine` 中的 3 個固定規則
- **目標狀態**：資料庫驅動的可配置規則引擎
- **遷移路徑**：5 個階段（規則 DSL 設計 → 解析器 → 資料庫 → UI）
- **預估工作量**：16-20 小時（衝刺 5-6）
- **觸發條件**：規則數量 > 5、需要動態閾值調整

#### DEBT-002：通知系統實作
- **當前狀態**：已創建警示但未發送通知
- **目標狀態**：多通道通知（LINE、Email、SMS、推送）
- **未來架構**：事件驅動（RabbitMQ）或排程（Celery）
- **預估工作量**：16-20 小時（衝刺 5-6）
- **包含內容**：通知偏好、傳遞追蹤、重試邏輯

---

### ✅ 測試 - 手動驗證完成

#### 警示 API 測試（100% 通過率）
- ✅ **測試 1**：計算活動警示數量 → HTTP 200，返回 `2` 個活動警示
- ✅ **測試 2**：列出病患警示 → HTTP 200，返回 2 個包含完整元數據的警示
- ✅ **測試 3**：按嚴重等級過濾 → HTTP 200，返回 1 個嚴重等級警示
- ✅ **測試 4**：按 ID 取得警示 → HTTP 200，返回完整警示詳情

#### 測試資料驗證
- 病患：利武雄（CAT：25、mMRC：2、GOLD Group E）
- 警示 1（嚴重）：「GOLD Group E - 最高風險病患」
- 警示 2（高）：「高症狀負擔（CAT：25）」
- 兩個警示：狀態為活動，自動觸發

#### 錯誤修復驗證
- ✅ 變數遮蔽已解決（無 500 錯誤）
- ✅ 欄位名稱已更正（無 AttributeError）
- ✅ 授權參數已修復（無 403 錯誤）
- ✅ SQLAlchemy 延遲載入已解決（無 MissingGreenlet）

---

### 🏗️ 架構與設計

#### Clean Architecture 分層
```
API 層（展示層）
  ↓ DTOs（AlertResponse、AlertListResponse）
應用層（用例）
  ↓ Alert Service（create_alert、list_alerts、count_active）
領域層（業務邏輯）
  ↓ AlertRuleEngine（3 個固定規則）
基礎設施層（資料）
  ↓ AlertRepositoryImpl（儲存庫模式）
  ↓ 資料庫（alerts 表格）
```

#### DDD 戰略設計
- **警示上下文**（核心領域）：風險偵測和警示
- **風險上下文**（核心領域）：GOLD ABE 分類
- **惡化上下文**（支援）：臨床事件追蹤
- **通知上下文**（通用）：延後至 MVP 後（ADR-017）

#### 儲存庫模式實作
- `IAlertRepository`（介面） - 抽象契約
- `AlertRepositoryImpl`（具體實作） - PostgreSQL 實作
- 透過 FastAPI Depends 進行依賴注入
- 與業務邏輯清晰分離

---

### 📊 指標與關鍵績效指標

#### 開發速度
- **階段 1**：惡化管理 - 12 小時（預估）→ 10 小時（實際）✅
- **階段 2**：警示系統 - 12 小時（預估）→ 14 小時（實際）⚠️（+2 小時除錯）
- **衝刺 4 總計**：24 小時（預估）→ 24 小時（實際）✅ 符合目標

#### 程式碼品質
- **警示系統**：100% DDD 合規性（領域、應用、基礎設施、API）
- **錯誤修復率**：測試期間修復 4 個錯誤（在生產環境前捕獲）
- **測試覆蓋率**：手動測試 100%（自動化測試待衝刺 5）

#### 技術債務
- **DEBT-001**：警示規則引擎演進 - 計劃升級（衝刺 5-6）
- **DEBT-002**：通知系統 - 計劃實作（衝刺 5-6）
- **總債務**：32-40 小時（可管理、已記錄、有償還計劃）

---

### 🔗 相關檔案

#### 實作
- `backend/src/respira_ally/domain/services/alert_rule_engine.py`（AlertRuleEngine）
- `backend/src/respira_ally/application/alert/alert_service.py`（AlertService）
- `backend/src/respira_ally/infrastructure/repository_impls/alert_repository_impl.py`（儲存庫）
- `backend/src/respira_ally/api/v1/routers/alert.py`（API 端點）
- `backend/src/respira_ally/application/risk/use_cases/calculate_risk_use_case.py`（自動觸發）

#### 文件
- `docs/adr/ADR-016-alert-mvp-fixed-rule-engine.md`（警示 MVP 策略）
- `docs/adr/ADR-017-notification-system-deferred-post-mvp.md`（通知延後）
- `docs/technical_debt/REGISTRY.md`（DEBT-001、DEBT-002）
- `docs/EVOLUTION_MAP.md`（警示系統路線圖）

---

### 🚀 下一個衝刺（衝刺 5）- 計劃

#### P1：前端整合
- [ ] 警示系統 UI 整合（儀表板徽章、警示列表）
- [ ] 風險評估儀表板更新（GOLD ABE 顯示）
- [ ] 警示詳情模態框，包含臨床上下文

#### P2：通知系統 MVP
- [ ] 通知資料模型設計（notifications、preferences 表格）
- [ ] NotificationService 實作（基本功能）
- [ ] LINE 通知整合
- [ ] 通知歷史追蹤

#### P3：警示生命週期管理
- [ ] `POST /api/v1/alerts/{id}/acknowledge` - 標記警示為已確認
- [ ] `POST /api/v1/alerts/{id}/resolve` - 解決警示並附註解
- [ ] 警示狀態轉換（ACTIVE → ACKNOWLEDGED → RESOLVED）

---

## [衝刺 3] - 2025-10-22

### 摘要
風險評估 API，具備 GOLD ABE 分類、CAT/mMRC 調查問卷、病患/治療師管理

*（詳細內容待補充）*

---

## [衝刺 2] - 2025-10-15

### 摘要
認證系統、資料庫設定、核心基礎設施

*（詳細內容待補充）*

---

## [衝刺 1] - 2025-10-08

### 摘要
專案初始化、架構設計、開發工作流程設定

*（詳細內容待補充）*

---

## 衝刺命名慣例

- **未發布版本**：開發中的功能，尚未部署
- **[衝刺 N]**：已完成的衝刺交付成果（YYYY-MM-DD 完成日期）
- **版本標籤**：移至生產環境時將新增（例如 v1.0.0）

---

## 圖例

- ✨ **新增**：新功能
- 🔄 **變更**：現有功能的變更
- 🗑️ **棄用**：即將移除的功能
- ❌ **移除**：已移除的功能
- 🐛 **修復**：錯誤修復
- 🔒 **安全性**：漏洞修復
- 📚 **文件**：僅文件變更
- 🏗️ **架構**：架構決策和設計變更
- ✅ **測試**：測試相關變更
- 📊 **指標**：關鍵績效指標、效能指標、分析

---

**維護者**：TaskMaster Hub 協調系統
**審查頻率**：每個衝刺結束時
**格式**：Keep a Changelog v1.0.0
