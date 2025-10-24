# ADR-014: 採用 GOLD 2011 ABE 分級系統取代自創評分模型

**狀態**: ✅ 已批准 (Accepted)
**日期**: 2025-10-24
**決策者**: Clinical Advisor, Technical Lead, Product Manager, TaskMaster Hub
**影響範圍**: Sprint 4 全面重新設計，ADR-013 重大修正，前端 UI 變更
**取代決策**: ADR-013 v1.0 (RCRS 加權評分模型)
**相關 ADR**: ADR-013 v2.0 (GOLD ABE 實作)

---

## 📋 背景 (Context)

### 問題描述

在 ADR-013 v1.0 中，我們設計了一套自創的 **RespiraAlly COPD Risk Score (RCRS)** 加權評分模型，使用 6 個因子計算 0-100 分的風險分數：

```
RCRS = 0.25×CAT + 0.20×mMRC + 0.20×Adherence
       + 0.15×Smoking + 0.10×Exercise + 0.10×Mood
```

然而，在與臨床顧問進一步討論後，發現此方案存在以下問題：

1. **缺乏臨床驗證**：
   - 權重 (0.25, 0.20, 0.15...) 基於文獻回顧，但未經台灣 COPD 族群驗證
   - 33/66 分界點無臨床依據，純粹三等分
   - 自創模型需要長期數據校正，短期內準確性無法保證

2. **偏離國際標準**：
   - GOLD (慢性阻塞性肺病全球倡議組織) 已有成熟的分級系統
   - 使用自創模型難以與國際研究比較
   - 治療師熟悉 GOLD 分級，自創模型增加認知負擔

3. **過度複雜**：
   - 6 個因子加權計算，調參困難
   - 需要 `risk_thresholds` 表動態配置權重
   - 需要複雜的 `alert_rules` 規則引擎

4. **缺少關鍵指標**：
   - 原設計未追蹤 **急性發作次數**
   - 無法判斷 GOLD C/D 群組（高急性發作風險）

### 臨床顧問建議

**顧問意見**：
> "建議直接採用 GOLD 2011 年修訂的 ABE 分級系統，這是國際認可的標準，已有大量臨床證據支持。自創評分模型需要至少 2-3 年的數據累積和驗證，不適合 MVP 階段。"

**GOLD 2011 ABE 分級標準**：
- **A級 (低風險)**: CAT<10 且 mMRC<2
- **B級 (中風險)**: CAT≥10 或 mMRC≥2
- **E級 (高風險)**: CAT≥10 且 mMRC≥2

**關鍵優勢**：
- 簡單：只需 CAT 和 mMRC 兩個指標
- 有效：已被全球廣泛驗證
- 標準：可與國際文獻直接比較

---

## 🎯 決策 (Decision)

### 採用 GOLD 2011 ABE 分級系統，放棄自創 RCRS 模型

#### 核心變更

| 項目 | ADR-013 v1.0 (❌ 放棄) | ADR-013 v2.0 (✅ 採用) |
|------|----------------------|----------------------|
| **分級系統** | RCRS (0-100 分) | GOLD ABE (A/B/E 級) |
| **計算邏輯** | 6 因子加權求和 | 2 因子邏輯判斷 |
| **風險等級** | 低/中/高 (33/66 分界) | A/B/E (固定邏輯) |
| **權重配置** | 需動態調整 (6 個權重) | 無需權重 |
| **急性發作** | ❌ 未追蹤 | ✅ 新增 exacerbations 表 |
| **規則引擎** | alert_rules 表 (複雜) | 固定 3 條規則 (簡單) |
| **工時估算** | 104h | **60h (-44h)** |
| **臨床依據** | 文獻拼湊，未驗證 | **GOLD 國際標準** |

#### 分級邏輯（極簡！）

```python
def calculate_gold_abe_group(cat_score: int, mmrc_grade: int) -> str:
    """
    GOLD 2011 ABE 分級邏輯

    參數:
    - cat_score: CAT 評估量表 (0-40)
    - mmrc_grade: mMRC 呼吸困難量表 (0-4)

    返回: 'A', 'B', 或 'E'
    """
    if cat_score < 10 and mmrc_grade < 2:
        return 'A'  # 低風險
    elif cat_score >= 10 and mmrc_grade >= 2:
        return 'E'  # 高風險
    else:
        return 'B'  # 中風險
```

**Linus 品味評分**：
- ✅ 無特殊情況（所有情況都被覆蓋）
- ✅ 無需權重調參
- ✅ 邏輯清晰（3 層 if-else，無嵌套）
- ✅ 可測試性高（3 個測試案例即可完整覆蓋）

#### 新增急性發作追蹤

為未來擴展至 GOLD ABCD 完整分級準備：

```sql
CREATE TABLE exacerbations (
    exacerbation_id UUID PRIMARY KEY,
    patient_id UUID NOT NULL,
    onset_date DATE NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('MILD', 'MODERATE', 'SEVERE')),
    required_hospitalization BOOLEAN DEFAULT FALSE,
    hospitalization_days INTEGER,
    ...
);

-- 患者表新增彙總欄位
ALTER TABLE patients
  ADD COLUMN exacerbation_count_last_12m INTEGER DEFAULT 0,
  ADD COLUMN hospitalization_count_last_12m INTEGER DEFAULT 0;
```

**GOLD C/D 判斷條件** (未來擴展)：
- 過去 12 個月急性發作 ≥2 次
- 或過去 12 個月因 COPD 住院 ≥1 次

---

## ⚖️ 後果分析 (Consequences)

### 正面影響 ✅

#### 1. 臨床有效性提升
- ✅ **國際標準**：GOLD 系統已被全球驗證，準確性有保證
- ✅ **治療師熟悉**：無需額外培訓，直接理解 A/B/E 分級
- ✅ **可比較性**：結果可與國際文獻直接比較

#### 2. 技術複雜度大幅降低
- ✅ **簡化計算**：從 6 因子加權 → 2 因子邏輯判斷
- ✅ **移除權重表**：不需要 risk_thresholds 配置
- ✅ **固定規則**：預警邏輯硬編碼，無需規則引擎
- ✅ **減少 44h 工時**：104h → 60h

#### 3. 可維護性提升
- ✅ **無需調參**：邏輯固定，不需臨床專家持續校正
- ✅ **測試簡單**：3 個測試案例即可完整覆蓋分級邏輯
- ✅ **bug 風險低**：邏輯簡單，不易出錯

#### 4. 擴展性預留
- ✅ **GOLD ABCD 準備**：已追蹤急性發作數據，未來可擴展至完整分級
- ✅ **輔助因子保留**：仍追蹤用藥遵從、吸菸、運動等因子，供治療師參考

### 挑戰與限制 ⚠️

#### 1. 功能範圍縮小
- ⚠️ **只用 2 個指標**：放棄用藥遵從、吸菸、運動等因子的自動評分
- **緩解**：這些因子仍會追蹤並顯示，供治療師手動判斷

#### 2. 個人化不足
- ⚠️ **固定邏輯**：無法根據個別病患調整權重
- **緩解**：GOLD 標準本就是通用分級，個人化由治療師專業判斷補足

#### 3. 機器學習延後
- ⚠️ **無 ML 模型**：原本計劃的加權模型可作為未來 ML 的基礎
- **緩解**：先累積 GOLD 分級數據，Phase 3 再訓練 ML 模型優化

#### 4. 前端 UI 需調整
- ⚠️ **已開發的 UI 需修改**：原本設計顯示 0-100 分，需改為 A/B/E 顯示
- **緩解**：實際上 Sprint 3 僅完成問卷，風險評分 UI 尚未開發

---

## 🔀 替代方案分析 (Alternatives Considered)

### 方案 A: 保留 RCRS 模型，但簡化為 3 因子 (❌ 未採用)

**提案**：保留加權模型，但只用 CAT、mMRC、急性發作 3 個因子

**優點**：
- 比 6 因子簡單
- 仍保留部分個人化空間

**缺點**：
- 仍需權重調參 (3 個權重總和 = 1.0)
- 仍需設定分界點 (33/66 或其他)
- 仍缺乏臨床驗證
- 仍偏離國際標準

**結論**：簡化不能解決根本問題（缺乏臨床驗證），不如直接用標準。

---

### 方案 B: 同時實作 RCRS 和 GOLD，讓治療師選擇 (❌ 未採用)

**提案**：提供兩套分級系統，治療師可切換

**優點**：
- 靈活性高
- 可比較兩套系統的表現

**缺點**：
- ❌ **開發成本加倍** (104h + 60h = 164h)
- ❌ **UI 複雜化** (需要切換介面)
- ❌ **治療師困惑** (不知道該信哪個)
- ❌ **維護負擔重** (兩套系統都要維護)

**結論**：違反 Linus "簡潔執念" 原則，過度設計。

---

### 方案 C: 採用 GOLD ABCD 完整分級（包含急性發作） (⏸ 暫不採用)

**提案**：直接實作 GOLD 2023 的完整 ABCD 分級

**優點**：
- 最完整的 GOLD 標準
- 包含急性發作風險評估

**缺點**：
- ❌ **數據不足**：需要累積至少 12 個月急性發作數據
- ❌ **初期無用**：新病患沒有歷史數據，無法判斷 C/D
- ⚠️ **工時增加**：需要實作急性發作風險判定邏輯

**結論**：MVP 階段先用 ABE，累積數據後 Sprint 6+ 擴展至 ABCD。

---

## 📚 參考文獻 (References)

1. **GOLD 2011 Report**: Global Strategy for Prevention, Diagnosis and Management of COPD (2011 Revision)
   - 引入 ABCD 分級系統（本專案採用 ABE 簡化版）
   - https://goldcopd.org/gold-reports/

2. **GOLD 2023 Report**: Global Strategy for Prevention, Diagnosis and Management of COPD
   - 最新版本，本專案未來將對齊
   - https://goldcopd.org/2023-gold-report-2/

3. **CAT Questionnaire Validation**: Jones PW, et al. (2009)
   - CAT ≥10 分為症狀較多的高風險群
   - Chest. 2009;135(6):1579-1586

4. **mMRC Scale Validation**: Fletcher CM (1960)
   - mMRC ≥2 視為呼吸困難嚴重
   - British Medical Journal, 1960;2:1665

5. **COPD Exacerbation Risk Assessment**: Hurst JR, et al. (2010)
   - 急性發作 ≥2次/年為高風險
   - New England Journal of Medicine. 2010;363(12):1128-1138

6. **台灣 COPD 臨床指引** (台灣胸腔暨重症加護醫學會)
   - 建議採用 GOLD 分級系統
   - 確認 ABE 分級在台灣族群的適用性

---

## 🔄 決策時間線 (Decision Timeline)

| 日期 | 事件 | 決策 |
|------|------|------|
| 2025-10-22 | ADR-013 v1.0 初版完成 | 設計 RCRS 加權模型 |
| 2025-10-24 | 與臨床顧問討論 | 發現 RCRS 缺乏驗證 |
| 2025-10-24 | 技術團隊評估 | GOLD ABE 可減少 44h 工時 |
| 2025-10-24 | 決策會議 | ✅ 採用 GOLD ABE，放棄 RCRS |
| 2025-10-24 | ADR-013 v2.0 發布 | 重大修正完成 |
| 2025-10-24 | ADR-014 建立 | 記錄決策變更原因（本文件） |

---

## 🎯 實施計畫 (Implementation Plan)

### Phase 1: 文檔更新 ✅ 已完成
- [x] ADR-013 v2.0 重大修正
- [x] ADR-014 建立（本文件）
- [ ] WBS 更新 (Sprint 4 工時 104h → 60h)

### Phase 2: 資料庫 Schema [8h]
- [ ] 建立 `exacerbations` 表
- [ ] 修改 `risk_scores` → `risk_assessments` 表
- [ ] 擴展 `patients` 表（急性發作彙總）
- [ ] 建立 trigger（自動更新統計）

### Phase 3: Backend API [24h]
- [ ] 急性發作管理 API (POST/GET/PUT /exacerbations)
- [ ] GOLD 分級 API (POST/GET /risk-assessments)
- [ ] 簡化預警 API (GET /alerts)

### Phase 4: Frontend UI [20h]
- [ ] 個案 360° 頁面：急性發作記錄區塊
- [ ] GOLD 分級卡片 (A/B/E 顯示)
- [ ] 預警中心頁面

### Phase 5: 驗證與測試 [8h]
- [ ] 與臨床專家確認邏輯正確性
- [ ] 單元測試 + 整合測試
- [ ] E2E 測試

**總計**: 60h (比原計劃減少 44h)

---

## 📊 成功指標 (Success Criteria)

### 技術指標
- [ ] GOLD 分級計算邏輯 100% 正確（與臨床專家驗證一致）
- [ ] 單元測試覆蓋率 ≥ 90%
- [ ] API 響應時間 < 200ms (P95)
- [ ] 急性發作數據追蹤完整（無遺漏）

### 業務指標
- [ ] 治療師理解 GOLD A/B/E 分級，無需額外培訓
- [ ] 高風險病患（E級）識別準確率 ≥ 95%
- [ ] 預警通知及時性：分級完成後 < 5 分鐘

### 未來擴展準備
- [ ] 累積 ≥ 100 位病患的 12 個月急性發作數據
- [ ] 為 GOLD ABCD 完整分級預留擴展點

---

## 💡 經驗教訓 (Lessons Learned)

### 1. "Never break userspace" - 向後相容 ✅
- 雖然是重大變更，但 Sprint 3 尚未實作風險評分 UI
- 只有 API 設計受影響，無破壞性變更
- **啟示**：早期發現問題，修正成本最低

### 2. "Practicality beats purity" - 實用主義 ✅
- 自創模型理論上可以更個人化，但實際上缺乏驗證數據
- GOLD 標準雖然簡單，但已被全球驗證，實用性高
- **啟示**：使用成熟方案，不要重新發明輪子

### 3. "Good taste eliminates special cases" - 簡潔設計 ✅
- 6 因子加權模型有太多特殊情況（數據缺漏、權重調整）
- GOLD ABE 只有 3 種情況，無特殊處理
- **啟示**：簡單的邏輯更可靠，更易維護

### 4. 早期臨床顧問參與的重要性 ⚠️
- 如果更早與臨床顧問討論，可避免 ADR-013 v1.0 的設計
- **改進**：未來重大決策需臨床顧問 +1 才能批准

---

## 🔗 相關文件

- [ADR-013 v2.0: COPD 風險引擎架構設計（GOLD ABE）](./ADR-013-copd-risk-engine-architecture.md)
- [16_wbs_development_plan.md](../16_wbs_development_plan.md) - Sprint 4 工時更新
- GOLD 2011 Official Report (外部連結)
- 台灣 COPD 臨床指引 (外部連結)

---

**決策批准簽名**:
- **Technical Lead**: ✅ 批准（技術簡化，工時減少）
- **Clinical Advisor**: ✅ 批准（符合國際標準，臨床有效）
- **Product Manager**: ✅ 批准（加速交付，降低風險）
- **TaskMaster Hub**: ✅ 批准（架構合理，可執行性高）

**文件版本**: v1.0
**建立日期**: 2025-10-24
**審查日期**: 2025-10-24
**狀態**: ✅ 已批准 (Accepted)

---

**Linus 最終評語**:
> "這才是正確的決策。不要在沒驗證的情況下發明複雜的演算法。用標準，用簡單的邏輯，先讓它跑起來。未來有數據了，再考慮優化。Talk is cheap, show me the working GOLD classifier."
