# ADR-017: Notification System Deferred to Post-MVP - 關注點分離

**狀態**: ✅ 已批准 (Accepted)
**日期**: 2025-10-26
**決策者**: Product Manager, Technical Lead, TaskMaster Hub
**影響範圍**: Alert System, Notification System, Architecture Layering
**實作時間**: 0h (Deferred Decision)
**相關檔案**:
- `domain/services/alert_rule_engine.py` (Alert creation logic)
- `application/alert/alert_service.py` (Alert persistence, NO notification)
- `api/v1/routers/notification.py` (Placeholder router, future implementation)
- `docs/technical_debt/REGISTRY.md` (DEBT-002: Notification System)

---

## 📋 背景 (Context)

### 問題描述

Sprint 4 交付 **Alert System MVP**，但完整的 Alert-to-Notification 流程需要決策：

**Alert System 職責** (Sprint 4 範圍):
- ✅ 評估病患風險並產生 Alert 記錄
- ✅ 儲存 Alert 至資料庫 (狀態: ACTIVE, ACKNOWLEDGED, RESOLVED)
- ✅ 提供 Alert API (GET list/detail/count)

**Notification System 職責** (範圍未定):
- ❓ 發送通知給治療師 (LINE, Email, SMS, Push Notification)
- ❓ 通知偏好設定 (哪些 Alert 發送、發送頻率、時段)
- ❓ 通知歷史記錄 (已發送、已讀、失敗重試)

**核心問題**:
> **Alert 創建後，是否應立即發送通知？**

---

## 🎯 決策 (Decision)

### 採用方案：**Deferred Notification - Alert 與 Notification 分離**

**核心設計原則** (Separation of Concerns):
> "Alert System 負責『偵測風險』，Notification System 負責『通知傳遞』。兩者應該是獨立的系統。"

#### 1. Alert System (Sprint 4 MVP) - 資料層

```python
# application/alert/alert_service.py
class AlertService:
    async def create_alert(self, alert_create: AlertCreate) -> AlertResponse:
        """
        Create alert record in database

        MVP Scope:
        - ✅ Persist alert to database
        - ✅ Return AlertResponse
        - ❌ NO notification sending (deferred to Post-MVP)

        Design:
        - Alert is a RECORD of detected risk
        - Notification is a DELIVERY mechanism
        - These are separate concerns
        """
        alert_model = AlertModel(**alert_create.model_dump(), status=AlertStatus.ACTIVE)
        self.db_session.add(alert_model)
        await self.db_session.commit()

        # ❌ NO: await self._send_notification(alert_model)
        # ✅ Alert created, stored, and queryable via API
        # ✅ Notification will be handled by separate NotificationService (Post-MVP)

        return AlertResponse.from_model(alert_model)
```

#### 2. Notification System (Post-MVP) - 通訊層

**未來架構** (Sprint 5+):

```python
# application/notification/notification_service.py
class NotificationService:
    """
    Notification delivery service (Post-MVP implementation)

    Responsibilities:
    - Send LINE/Email/SMS/Push notifications
    - Handle notification preferences (which alerts to send, frequency, time window)
    - Track notification history (sent, delivered, read, failed)
    - Retry failed notifications

    Trigger Mechanisms (to be decided):
    Option 1: Event-Driven (RabbitMQ)
        - AlertService publishes "AlertCreated" event
        - NotificationService subscribes and sends notifications

    Option 2: Scheduled Job (Celery/APScheduler)
        - Periodic task checks for new ACTIVE alerts
        - Sends notifications for alerts created in last N minutes

    Option 3: Real-Time Trigger (Immediate)
        - AlertService calls NotificationService.send_notification()
        - Synchronous or async queue
    """

    async def send_alert_notification(
        self,
        alert: AlertResponse,
        recipient: TherapistProfile,
        channels: list[NotificationChannel],
    ) -> NotificationResponse:
        """Send alert notification via specified channels"""
        pass  # Future implementation

# alembic/versions/XXX_add_notification_tables.py
CREATE TABLE development.notifications (
    notification_id UUID PRIMARY KEY,
    alert_id UUID REFERENCES alerts(alert_id),
    recipient_id UUID REFERENCES users(user_id),
    channel VARCHAR(20),  -- LINE, EMAIL, SMS, PUSH
    status VARCHAR(20),   -- PENDING, SENT, DELIVERED, READ, FAILED
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    retry_count INT DEFAULT 0
);

CREATE TABLE development.notification_preferences (
    user_id UUID REFERENCES users(user_id),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    enabled BOOLEAN DEFAULT TRUE,
    channels JSONB,  -- ["LINE", "EMAIL"]
    quiet_hours JSONB  -- {"start": "22:00", "end": "08:00"}
);
```

#### 3. 分離設計優勢 (Separation Benefits)

| 面向 | Alert System | Notification System |
|------|--------------|---------------------|
| **職責** | 偵測風險，儲存記錄 | 傳遞通知，追蹤狀態 |
| **資料模型** | alerts table | notifications, notification_preferences |
| **依賴** | Risk Assessment | Alerts, LINE API, Email Service |
| **失敗影響** | 風險偵測失敗 | 通知發送失敗 (不影響 Alert 記錄) |
| **測試** | 規則邏輯測試 | 通知發送測試 (需 mock LINE API) |
| **擴展性** | 新增規則 | 新增通知通道 (SMS, Push) |

---

## ✅ 優點 (Pros)

### 關注點分離 (Separation of Concerns)
- **獨立演進**: Alert 規則邏輯變更不影響 Notification 發送
- **獨立測試**: 可單獨測試 Alert 創建和 Notification 發送
- **獨立部署**: 可將 Notification Service 部署為獨立微服務

### 簡化 MVP
- **專注驗證**: Sprint 4 專注於驗證 Alert 規則的臨床價值
- **降低風險**: 不需整合 LINE API, Email Service (減少外部依賴)
- **加速交付**: 減少 8-12h 開發時間 (Notification integration)

### 未來靈活性
- **多通道支援**: 未來可支援 LINE, Email, SMS, Push Notification
- **通知偏好**: 用戶可自訂哪些 Alert 發送通知、發送頻率
- **批量通知**: 可實作 "Daily Digest" (每日彙總通知)

---

## ❌ 缺點 (Cons)

### 用戶體驗延遲
- **無即時通知**: Alert 創建後，治療師無法立即收到通知
- **需主動查看**: 治療師需登入 Dashboard 查看 Alert 列表
- **錯過風險**: 高風險 Alert 可能被延遲發現

**緩解措施**:
- Dashboard 顯示 Alert badge (未讀數量)
- Alert list 按 severity 和 triggered_at 排序 (CRITICAL 優先)
- MVP 期間，治療師接受定期登入查看 (臨床流程調整)

### 功能不完整
- **MVP 限制**: Alert System 功能不完整，缺少通知環節
- **需後續開發**: Sprint 5+ 需投入額外時間實作 Notification

### 技術債務
- **DEBT-002**: Notification System Implementation
  - 預估開發時間：16-20h (Sprint 5-6)
  - 包含：Notification Service, LINE/Email integration, Notification Preferences UI

---

## 🔄 替代方案 (Alternatives Considered)

### 方案 A: Alert 創建時立即發送通知 (Immediate Notification)

**實作方式**:
```python
class AlertService:
    async def create_alert(self, alert_create: AlertCreate) -> AlertResponse:
        alert_model = AlertModel(**alert_create.model_dump())
        self.db_session.add(alert_model)
        await self.db_session.commit()

        # 立即發送通知
        notification_service = NotificationService()
        await notification_service.send_alert_notification(
            alert=alert_model,
            recipient=alert_model.patient.therapist,
            channels=["LINE", "EMAIL"]
        )

        return AlertResponse.from_model(alert_model)
```

**評估**:
- ✅ 用戶體驗完整，即時通知
- ❌ 增加 8-12h 開發時間 (LINE/Email integration)
- ❌ 外部依賴增加 (LINE API, Email Service)
- ❌ 失敗處理複雜 (通知失敗是否影響 Alert 創建？)
- ❌ **Result**: 不適合 MVP，推遲至 Sprint 5

### 方案 B: 事件驅動 Notification (Event-Driven)

**實作方式**:
```python
class AlertService:
    async def create_alert(self, alert_create: AlertCreate) -> AlertResponse:
        alert_model = AlertModel(**alert_create.model_dump())
        self.db_session.add(alert_model)
        await self.db_session.commit()

        # 發布事件到 RabbitMQ
        await event_publisher.publish(
            event=AlertCreatedEvent(alert_id=alert_model.alert_id),
            exchange="alerts",
            routing_key="alert.created"
        )

        return AlertResponse.from_model(alert_model)

# 獨立 Notification Worker 訂閱事件
class NotificationWorker:
    async def on_alert_created(self, event: AlertCreatedEvent):
        alert = await alert_service.get_alert_by_id(event.alert_id)
        await notification_service.send_alert_notification(alert)
```

**評估**:
- ✅ 完全解耦 Alert 和 Notification
- ✅ 支援異步處理，不阻塞 Alert 創建
- ✅ 易於擴展 (新增 subscriber 處理其他事件)
- ❌ 需要 RabbitMQ integration (已有基礎設施，但需額外開發)
- ❌ 增加系統複雜度 (Event Schema, Message Queue)
- 🔮 **Result**: 優秀方案，但推遲至 Sprint 6+ (Event-Driven Architecture 升級)

---

## 📊 影響分析 (Impact)

### 功能影響
| 功能 | 影響 | 說明 |
|------|------|------|
| Alert API | ✅ 完整 | GET list/detail/count endpoints 正常運作 |
| Dashboard Alert Badge | ✅ 支援 | 前端可查詢 active alert count 並顯示 badge |
| Alert List UI | ✅ 支援 | 前端可顯示 Alert 列表 (by severity, date) |
| LINE Notification | ❌ 延後 | MVP 不發送 LINE 通知 |
| Email Notification | ❌ 延後 | MVP 不發送 Email 通知 |
| Notification Preferences | ❌ 延後 | MVP 無通知偏好設定 |

### 用戶體驗影響
- **治療師**: 需定期登入 Dashboard 查看 Alert，無即時通知
- **病患**: 無影響 (病患不接收 Alert 通知，由治療師主動聯繫)

### 開發影響
- **Sprint 4**: 節省 8-12h 開發時間，專注於 Alert 規則邏輯
- **Sprint 5+**: 需投入 16-20h 實作 Notification System

---

## 🎓 經驗教訓 (Lessons Learned)

### Linus Torvalds 哲學應用

**"Don't overdesign."**
- MVP 不需要完美的通知系統
- 先驗證 Alert 規則的臨床價值
- 再優化通知傳遞機制

**"Separation of mechanism and policy."**
- Alert (mechanism): 偵測風險
- Notification (policy): 如何通知、何時通知、通知誰

### 分階段交付策略

**Good Product Strategy**:
1. **Sprint 4 (MVP)**: Alert System - 驗證風險偵測邏輯
2. **Sprint 5**: Notification System - 基本通知功能 (LINE)
3. **Sprint 6**: Notification Preferences - 進階偏好設定
4. **Sprint 7**: Event-Driven Architecture - 完全解耦

---

## 📝 決策驗證標準 (Validation Criteria)

### Sprint 4 MVP 成功標準
- [ ] ✅ Alert 成功創建並儲存至資料庫 (已驗證)
- [ ] ✅ Alert API 返回正確資料 (已驗證)
- [ ] ✅ Dashboard 顯示 Alert badge 和列表 (待前端整合)
- [ ] ✅ 治療師接受「手動查看 Alert」的臨床流程 (待驗證)

### Sprint 5 Notification 實作觸發條件
- [ ] 治療師反饋：「手動查看 Alert 效率太低」
- [ ] 臨床數據：Alert 平均被發現時間 > 2 小時 (影響及時性)
- [ ] 業務需求：需支援多通道通知 (LINE, Email)

---

## 🔗 相關文件 (Related Documents)

- **ADR-016**: Alert MVP Fixed Rule Engine (Alert 規則邏輯)
- **ADR-004**: LINE as Patient Entrypoint (LINE integration 基礎)
- **ADR-005**: RabbitMQ for Message Queue (Event-Driven 基礎設施)
- **DEBT-002**: Notification System Implementation (Technical Debt Registry)
- **EVOLUTION_MAP.md**: Notification System 演進路線圖

---

## 🚀 下一步 (Next Steps)

### Sprint 4 (Current - Alert Only)
- [x] ✅ Alert System 實作完成 (no notification)
- [x] ✅ Alert API 測試驗證通過
- [ ] 📋 前端整合 Alert badge 和列表 UI
- [ ] 📋 治療師臨床流程培訓 (手動查看 Alert)

### Sprint 5 (Notification MVP)
- [ ] 📋 設計 Notification data model (notifications, notification_preferences)
- [ ] 📋 實作 NotificationService (基本功能)
- [ ] 📋 LINE Notification integration
- [ ] 📋 Notification history tracking
- [ ] 📋 簡單的 Notification Preferences (enable/disable by alert type)

### Sprint 6+ (Advanced Notification)
- [ ] 🔮 Email/SMS Notification 支援
- [ ] 🔮 Notification Preferences UI (時段、頻率、通道)
- [ ] 🔮 Batch Notification (Daily Digest)
- [ ] 🔮 Event-Driven Architecture (RabbitMQ-based notification)

### Sprint 7+ (Event-Driven Architecture)
- [ ] 🔮 Alert System 發布 "AlertCreated" event to RabbitMQ
- [ ] 🔮 Notification Worker 訂閱事件並發送通知
- [ ] 🔮 其他 Workers 訂閱 Alert events (Analytics, Reporting)

---

**簽核**: TaskMaster Hub Coordination (2025-10-26)
**技術審查**: Separation of Concerns Applied ✅
**業務審查**: MVP Scope Validated, Post-MVP Roadmap Defined ✅
**風險管理**: User Experience Trade-off Documented ✅
