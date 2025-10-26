# 並行開發計劃 - Alert UI + Task Management System

**文件版本**: v1.0
**創建日期**: 2025-10-27
**適用 Sprint**: Sprint 5
**預估總時程**: 24-32 小時（並行執行可縮短至 24-28 小時）
**開發模式**: 雙軌並行（Frontend + Backend）

---

## 🎯 核心策略：Linus 式並行開發

> **Linus Torvalds**: "Bad programmers worry about the code. Good programmers worry about data structures and their relationships."

### 並行開發的關鍵原則

1. **清晰的責任邊界** - 前後端完全解耦，避免代碼衝突
2. **最小化依賴** - Role A 使用已完成的 Alert API，Role B 開發獨立的 Task API
3. **持續整合** - 每日至少一次整合，避免大爆炸式合併
4. **單一事實來源** - 所有 API 契約在 `docs/06_api_design_specification.md` 中定義

---

## 👥 開發角色定義

### 🔷 **Role A - Frontend Developer (Alert UI Specialist)**

**核心職責**: 讓已完成的 Alert System 後端功能立即可用

**技術堆棧**:
- React 18+ / TypeScript
- Ant Design (UI Component Library)
- React Query / SWR (Data Fetching)
- React Router (Routing)

**工作範圍**:
```
frontend/src/
├── components/
│   └── alert/              ← Role A 負責
│       ├── AlertList.tsx
│       ├── AlertDetail.tsx
│       └── AlertBadge.tsx
├── services/
│   └── alertService.ts     ← Role A 負責
├── types/
│   └── alert.ts            ← Role A 負責
└── pages/
    └── AlertPage.tsx       ← Role A 負責
```

**預估工時**: 8 小時（可在 1-2 個工作日內完成）

---

### 🔶 **Role B - Backend Developer (Task Management Specialist)**

**核心職責**: 實作 Task Management System 從領域層到 API 層的完整功能

**技術堆棧**:
- Python 3.11+ / FastAPI
- SQLAlchemy 2.0 (ORM)
- Pydantic (Data Validation)
- PostgreSQL 15+

**工作範圍**:
```
backend/src/respira_ally/
├── domain/
│   ├── entities/
│   │   └── task.py         ← Role B 負責
│   └── services/
│       └── task_service.py ← Role B 負責
├── application/
│   └── task/
│       ├── use_cases/      ← Role B 負責
│       └── task_service.py ← Role B 負責
├── infrastructure/
│   ├── models/
│   │   └── task_model.py   ← Role B 負責
│   └── repository_impls/
│       └── task_repository_impl.py ← Role B 負責
└── api/v1/
    └── routers/
        └── task.py          ← Role B 負責
```

**預估工時**: 24 小時（可在 3-4 個工作日內完成）

---

## 📅 並行開發時程規劃

### Timeline - 以 4 個工作日為例

```
Day 1 (8h)
  Role A: A1 Alert List Component [3h] + A2 Alert Detail Modal [2h] + A3 Badge [2h]
  Role B: B1 Task Entity [4h] + B2 Repository [3h] (開始)

Day 2 (8h)
  Role A: A4 API Integration Test [1h] + Code Review + Bug Fix [3h] + Documentation [2h]
  Role B: B2 Repository (完成) [1h] + B3 Task API Endpoints [5h] + B4 Auto-generation (開始) [2h]

Day 3 (8h)
  Role A: 待命協助整合測試 / 開始 Task Board UI 前期準備 [2h]
  Role B: B4 Auto-generation (完成) [6h] + B5 Assignment Logic [2h]

Day 4 (8h)
  Role A: Task Board UI 開發 [4h] (依賴 B 完成 API)
  Role B: B5 Assignment Logic (完成) [2h] + Testing [4h]
  整合: E2E Testing [2h]
```

**關鍵里程碑**:
- ✅ Day 2 End: Alert UI 完全可用（8h）
- ✅ Day 4 End: Task Management 後端完成（24h）
- ✅ Day 5: Task Board UI + E2E Testing（4h）

---

## 🔧 並行開發 Checklist

### 📋 Role A - Frontend Developer Checklist

#### **Pre-Development (開發前)**
- [ ] **環境設定**
  - [ ] 確認 Node.js 版本 >= 18.x (`node --version`)
  - [ ] 確認後端 API 可訪問 (`curl http://localhost:8000/api/v1/health`)
  - [ ] 安裝前端依賴 (`npm install`)
  - [ ] 啟動開發服務器 (`npm run dev`)

- [ ] **API 契約確認**
  - [ ] 閱讀 Alert API 文檔 (`docs/06_api_design_specification.md` - Alert 章節)
  - [ ] 使用 Postman/curl 測試 3 個 Alert 端點：
    - [ ] `GET /api/v1/alerts/patients/{patient_id}/` (列表)
    - [ ] `GET /api/v1/alerts/patients/{patient_id}/active/count` (計數)
    - [ ] `GET /api/v1/alerts/{alert_id}` (詳情)

- [ ] **Git 分支建立**
  - [ ] 從 `dev` 分支建立 `feature/alert-ui` 分支
  - [ ] 設定 upstream: `git push -u origin feature/alert-ui`

---

#### **Phase A1 - Alert List Component [3h]**

**目標**: 實作 Alert 列表頁面，支援過濾、分頁、排序

**檔案清單**:
```typescript
// 1. Type Definitions
frontend/src/types/alert.ts

// 2. API Service
frontend/src/services/alertService.ts

// 3. Component
frontend/src/components/alert/AlertList.tsx

// 4. Page
frontend/src/pages/AlertPage.tsx
```

**實作 Checklist**:
- [ ] **Step 1 - Type Definitions** [30min]
  ```typescript
  // frontend/src/types/alert.ts
  export enum AlertType {
    GOLD_GROUP_E = 'GOLD_GROUP_E',
    HIGH_CAT_SCORE = 'HIGH_CAT_SCORE',
    FREQUENT_EXACERBATIONS = 'FREQUENT_EXACERBATIONS'
  }

  export enum AlertSeverity {
    CRITICAL = 'CRITICAL',
    HIGH = 'HIGH',
    MEDIUM = 'MEDIUM',
    LOW = 'LOW'
  }

  export enum AlertStatus {
    ACTIVE = 'ACTIVE',
    ACKNOWLEDGED = 'ACKNOWLEDGED',
    RESOLVED = 'RESOLVED'
  }

  export interface Alert {
    alert_id: string;
    patient_id: string;
    alert_type: AlertType;
    severity: AlertSeverity;
    status: AlertStatus;
    triggered_at: string;
    metadata: Record<string, any>;
  }

  export interface AlertListResponse {
    alerts: Alert[];
    total: number;
    page: number;
    page_size: number;
  }
  ```

- [ ] **Step 2 - API Service** [30min]
  ```typescript
  // frontend/src/services/alertService.ts
  import { Alert, AlertListResponse } from '@/types/alert';

  export const alertService = {
    // 取得病患 Alert 列表
    async getPatientAlerts(
      patientId: string,
      params?: {
        alert_type?: string;
        severity?: string;
        status?: string;
        page?: number;
        page_size?: number;
      }
    ): Promise<AlertListResponse> {
      const queryParams = new URLSearchParams(params as any).toString();
      const response = await fetch(
        `/api/v1/alerts/patients/${patientId}/?${queryParams}`
      );
      return response.json();
    },

    // 取得活動 Alert 計數
    async getActiveAlertCount(patientId: string): Promise<number> {
      const response = await fetch(
        `/api/v1/alerts/patients/${patientId}/active/count`
      );
      const data = await response.json();
      return data.active_count;
    },

    // 取得 Alert 詳情
    async getAlertById(alertId: string): Promise<Alert> {
      const response = await fetch(`/api/v1/alerts/${alertId}`);
      return response.json();
    }
  };
  ```

- [ ] **Step 3 - Alert List Component** [1.5h]
  ```typescript
  // frontend/src/components/alert/AlertList.tsx
  import React, { useState, useEffect } from 'react';
  import { Table, Tag, Select, DatePicker, Space } from 'antd';
  import { alertService } from '@/services/alertService';
  import { Alert, AlertSeverity, AlertStatus } from '@/types/alert';

  const AlertList: React.FC<{ patientId: string }> = ({ patientId }) => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({ page: 0, pageSize: 20, total: 0 });
    const [filters, setFilters] = useState({});

    // 載入 Alert 列表
    const loadAlerts = async () => {
      setLoading(true);
      try {
        const response = await alertService.getPatientAlerts(patientId, {
          page: pagination.page,
          page_size: pagination.pageSize,
          ...filters
        });
        setAlerts(response.alerts);
        setPagination(prev => ({ ...prev, total: response.total }));
      } finally {
        setLoading(false);
      }
    };

    useEffect(() => {
      loadAlerts();
    }, [patientId, pagination.page, pagination.pageSize, filters]);

    // Severity 顏色映射
    const getSeverityColor = (severity: AlertSeverity) => {
      const colors = {
        CRITICAL: 'red',
        HIGH: 'orange',
        MEDIUM: 'gold',
        LOW: 'blue'
      };
      return colors[severity] || 'default';
    };

    // Table 欄位定義
    const columns = [
      {
        title: 'Alert Type',
        dataIndex: 'alert_type',
        key: 'alert_type',
        render: (type: string) => <Tag>{type.replace(/_/g, ' ')}</Tag>
      },
      {
        title: 'Severity',
        dataIndex: 'severity',
        key: 'severity',
        render: (severity: AlertSeverity) => (
          <Tag color={getSeverityColor(severity)}>{severity}</Tag>
        )
      },
      {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        render: (status: AlertStatus) => (
          <Tag color={status === 'ACTIVE' ? 'red' : 'green'}>{status}</Tag>
        )
      },
      {
        title: 'Triggered At',
        dataIndex: 'triggered_at',
        key: 'triggered_at',
        render: (date: string) => new Date(date).toLocaleString()
      }
    ];

    return (
      <div>
        {/* 過濾器 */}
        <Space style={{ marginBottom: 16 }}>
          <Select
            placeholder="Filter by Severity"
            style={{ width: 200 }}
            onChange={(value) => setFilters(prev => ({ ...prev, severity: value }))}
            allowClear
          >
            <Select.Option value="CRITICAL">Critical</Select.Option>
            <Select.Option value="HIGH">High</Select.Option>
            <Select.Option value="MEDIUM">Medium</Select.Option>
          </Select>

          <Select
            placeholder="Filter by Status"
            style={{ width: 200 }}
            onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
            allowClear
          >
            <Select.Option value="ACTIVE">Active</Select.Option>
            <Select.Option value="ACKNOWLEDGED">Acknowledged</Select.Option>
            <Select.Option value="RESOLVED">Resolved</Select.Option>
          </Select>
        </Space>

        {/* Alert 列表 */}
        <Table
          dataSource={alerts}
          columns={columns}
          loading={loading}
          rowKey="alert_id"
          pagination={{
            current: pagination.page + 1,
            pageSize: pagination.pageSize,
            total: pagination.total,
            onChange: (page, pageSize) => {
              setPagination(prev => ({ ...prev, page: page - 1, pageSize }));
            }
          }}
        />
      </div>
    );
  };

  export default AlertList;
  ```

- [ ] **Step 4 - Integration Test** [30min]
  - [ ] 使用真實 API 測試（`npm run dev` + 後端運行）
  - [ ] 驗證過濾功能（Severity, Status）
  - [ ] 驗證分頁功能
  - [ ] 驗證 Loading 狀態

---

#### **Phase A2 - Alert Detail Modal [2h]**

**目標**: 點擊 Alert 行顯示詳細資訊彈窗

**實作 Checklist**:
- [ ] **Step 1 - Alert Detail Component** [1h]
  ```typescript
  // frontend/src/components/alert/AlertDetail.tsx
  import React from 'react';
  import { Modal, Descriptions, Tag, Typography } from 'antd';
  import { Alert } from '@/types/alert';

  interface AlertDetailProps {
    alert: Alert | null;
    visible: boolean;
    onClose: () => void;
  }

  const AlertDetail: React.FC<AlertDetailProps> = ({ alert, visible, onClose }) => {
    if (!alert) return null;

    return (
      <Modal
        title="Alert Details"
        open={visible}
        onCancel={onClose}
        footer={null}
        width={800}
      >
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Alert ID">{alert.alert_id}</Descriptions.Item>
          <Descriptions.Item label="Patient ID">{alert.patient_id}</Descriptions.Item>
          <Descriptions.Item label="Alert Type">
            <Tag>{alert.alert_type}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Severity">
            <Tag color="red">{alert.severity}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={alert.status === 'ACTIVE' ? 'red' : 'green'}>
              {alert.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Triggered At">
            {new Date(alert.triggered_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>

        <Typography.Title level={5} style={{ marginTop: 24 }}>
          Metadata
        </Typography.Title>
        <pre>{JSON.stringify(alert.metadata, null, 2)}</pre>
      </Modal>
    );
  };

  export default AlertDetail;
  ```

- [ ] **Step 2 - 整合到 AlertList** [30min]
  ```typescript
  // 在 AlertList.tsx 中添加
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  // 添加到 Table props
  onRow={(record) => ({
    onClick: () => {
      setSelectedAlert(record);
      setModalVisible(true);
    },
    style: { cursor: 'pointer' }
  })}

  // 添加 Modal
  <AlertDetail
    alert={selectedAlert}
    visible={modalVisible}
    onClose={() => setModalVisible(false)}
  />
  ```

- [ ] **Step 3 - 測試互動** [30min]
  - [ ] 點擊 Alert 行觸發 Modal
  - [ ] 驗證 Metadata 顯示正確
  - [ ] 測試關閉 Modal

---

#### **Phase A3 - Dashboard Alert Badge [2h]**

**目標**: 在 Dashboard 顯示活動 Alert 數量徽章

**實作 Checklist**:
- [ ] **Step 1 - Alert Badge Component** [1h]
  ```typescript
  // frontend/src/components/alert/AlertBadge.tsx
  import React, { useEffect, useState } from 'react';
  import { Badge, Tooltip } from 'antd';
  import { BellOutlined } from '@ant-design/icons';
  import { alertService } from '@/services/alertService';

  interface AlertBadgeProps {
    patientId: string;
  }

  const AlertBadge: React.FC<AlertBadgeProps> = ({ patientId }) => {
    const [count, setCount] = useState(0);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
      const loadCount = async () => {
        setLoading(true);
        try {
          const activeCount = await alertService.getActiveAlertCount(patientId);
          setCount(activeCount);
        } finally {
          setLoading(false);
        }
      };

      loadCount();
      // 每 60 秒刷新一次
      const interval = setInterval(loadCount, 60000);
      return () => clearInterval(interval);
    }, [patientId]);

    return (
      <Tooltip title={`${count} active alerts`}>
        <Badge count={count} offset={[10, 0]}>
          <BellOutlined style={{ fontSize: 24 }} />
        </Badge>
      </Tooltip>
    );
  };

  export default AlertBadge;
  ```

- [ ] **Step 2 - 整合到 Dashboard** [30min]
  - [ ] 在 PatientTable 或 Dashboard 添加 AlertBadge
  - [ ] 確認點擊 Badge 跳轉到 AlertPage

- [ ] **Step 3 - 測試自動刷新** [30min]
  - [ ] 驗證初始載入顯示正確計數
  - [ ] 驗證每 60 秒自動刷新

---

#### **Phase A4 - API Integration Testing [1h]**

**整合測試 Checklist**:
- [ ] **端到端測試**
  - [ ] 測試完整 Alert 查詢流程
  - [ ] 測試過濾功能（各種組合）
  - [ ] 測試分頁跳轉
  - [ ] 測試 Alert 詳情顯示

- [ ] **錯誤處理測試**
  - [ ] 測試 API 失敗場景（關閉後端）
  - [ ] 測試授權失敗（無效 Token）
  - [ ] 測試空數據場景（無 Alert）

- [ ] **效能測試**
  - [ ] 測試大量 Alert（>100）的渲染效能
  - [ ] 測試快速切換過濾的響應速度

---

#### **Role A - Git Workflow**

**每日提交規範**:
```bash
# Day 1 結束
git add .
git commit -m "feat(frontend): implement Alert List Component

- Add AlertList component with filter and pagination
- Add alertService for API integration
- Add alert type definitions

Component covers:
- Alert listing with Ant Design Table
- Severity and Status filtering
- Pagination support"

git push origin feature/alert-ui

# Day 2 結束
git add .
git commit -m "feat(frontend): complete Alert UI integration

- Add AlertDetail modal for detailed view
- Add AlertBadge for Dashboard
- Add E2E integration tests

Alert UI is now fully functional and ready for production"

git push origin feature/alert-ui
```

---

### 📋 Role B - Backend Developer Checklist

#### **Pre-Development (開發前)**
- [ ] **環境設定**
  - [ ] 確認 Python 版本 >= 3.11 (`python --version`)
  - [ ] 啟動虛擬環境 (`source venv/bin/activate` 或 `poetry shell`)
  - [ ] 確認資料庫可訪問 (`psql -U admin -d respirally_db`)
  - [ ] 執行資料庫遷移 (`alembic upgrade head`)

- [ ] **DDD 架構確認**
  - [ ] 閱讀現有 Alert System 架構 (`backend/src/respira_ally/domain/services/alert_rule_engine.py`)
  - [ ] 確認 Repository Pattern 實作 (`backend/src/respira_ally/infrastructure/repository_impls/alert_repository_impl.py`)
  - [ ] 理解 Use Case 模式 (`backend/src/respira_ally/application/risk/use_cases/`)

- [ ] **Git 分支建立**
  - [ ] 從 `dev` 分支建立 `feature/task-management` 分支
  - [ ] 設定 upstream: `git push -u origin feature/task-management`

---

#### **Phase B1 - Task Entity 設計與實作 [4h]**

**目標**: 遵循 DDD 設計 Task 領域實體和資料模型

**檔案清單**:
```python
# 1. Domain Entity
backend/src/respira_ally/domain/entities/task.py

# 2. Database Model
backend/src/respira_ally/infrastructure/models/task_model.py

# 3. Repository Interface
backend/src/respira_ally/domain/repositories/i_task_repository.py

# 4. Migration Script
backend/alembic/versions/xxxx_create_tasks_table.py
```

**實作 Checklist**:
- [ ] **Step 1 - Domain Entity** [1.5h]
  ```python
  # backend/src/respira_ally/domain/entities/task.py
  from dataclasses import dataclass
  from datetime import datetime
  from enum import Enum
  from typing import Optional
  from uuid import UUID

  class TaskPriority(str, Enum):
      CRITICAL = "CRITICAL"
      HIGH = "HIGH"
      MEDIUM = "MEDIUM"
      LOW = "LOW"

  class TaskStatus(str, Enum):
      TODO = "TODO"
      IN_PROGRESS = "IN_PROGRESS"
      DONE = "DONE"
      CANCELLED = "CANCELLED"

  @dataclass
  class Task:
      """Task Domain Entity - 代表治療師需要執行的任務"""

      task_id: UUID
      title: str
      description: Optional[str]
      priority: TaskPriority
      status: TaskStatus
      patient_id: UUID
      assigned_to: Optional[UUID]  # therapist_id
      related_alert_id: Optional[UUID]  # 關聯的 Alert
      created_at: datetime
      updated_at: datetime
      due_date: Optional[datetime]
      completed_at: Optional[datetime]

      def assign_to(self, therapist_id: UUID) -> None:
          """分配任務給治療師"""
          if self.status == TaskStatus.DONE:
              raise ValueError("Cannot assign completed task")
          self.assigned_to = therapist_id
          self.updated_at = datetime.utcnow()

      def start(self) -> None:
          """開始執行任務"""
          if self.status != TaskStatus.TODO:
              raise ValueError(f"Cannot start task in {self.status} status")
          self.status = TaskStatus.IN_PROGRESS
          self.updated_at = datetime.utcnow()

      def complete(self) -> None:
          """完成任務"""
          if self.status != TaskStatus.IN_PROGRESS:
              raise ValueError(f"Cannot complete task in {self.status} status")
          self.status = TaskStatus.DONE
          self.completed_at = datetime.utcnow()
          self.updated_at = datetime.utcnow()

      def cancel(self) -> None:
          """取消任務"""
          if self.status == TaskStatus.DONE:
              raise ValueError("Cannot cancel completed task")
          self.status = TaskStatus.CANCELLED
          self.updated_at = datetime.utcnow()

      @property
      def is_overdue(self) -> bool:
          """檢查任務是否逾期"""
          if not self.due_date or self.status == TaskStatus.DONE:
              return False
          return datetime.utcnow() > self.due_date
  ```

- [ ] **Step 2 - Database Model** [1.5h]
  ```python
  # backend/src/respira_ally/infrastructure/models/task_model.py
  from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
  from sqlalchemy.dialects.postgresql import UUID
  from sqlalchemy.orm import relationship
  from datetime import datetime
  import uuid

  from respira_ally.infrastructure.models.base import Base
  from respira_ally.domain.entities.task import TaskPriority, TaskStatus

  class TaskModel(Base):
      __tablename__ = "tasks"
      __table_args__ = {"schema": "development"}

      # Primary Key
      task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

      # Task Information
      title = Column(String(200), nullable=False, comment="任務標題")
      description = Column(Text, nullable=True, comment="任務描述")
      priority = Column(
          SQLEnum(TaskPriority, name="task_priority"),
          nullable=False,
          default=TaskPriority.MEDIUM,
          comment="任務優先級"
      )
      status = Column(
          SQLEnum(TaskStatus, name="task_status"),
          nullable=False,
          default=TaskStatus.TODO,
          comment="任務狀態"
      )

      # Relations
      patient_id = Column(
          UUID(as_uuid=True),
          ForeignKey("development.patient_profiles.patient_id"),
          nullable=False,
          comment="關聯病患"
      )
      assigned_to = Column(
          UUID(as_uuid=True),
          ForeignKey("development.therapist_profiles.therapist_id"),
          nullable=True,
          comment="分配治療師"
      )
      related_alert_id = Column(
          UUID(as_uuid=True),
          ForeignKey("development.alerts.alert_id"),
          nullable=True,
          comment="關聯 Alert"
      )

      # Timestamps
      created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
      updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
      due_date = Column(DateTime, nullable=True, comment="截止日期")
      completed_at = Column(DateTime, nullable=True, comment="完成時間")

      # Relationships
      patient = relationship("PatientProfileModel", back_populates="tasks")
      therapist = relationship("TherapistProfileModel", back_populates="assigned_tasks")
      related_alert = relationship("AlertModel", back_populates="tasks")

      def __repr__(self):
          return f"<Task(id={self.task_id}, title='{self.title}', status={self.status})>"
  ```

- [ ] **Step 3 - Alembic Migration** [1h]
  ```bash
  # 生成遷移腳本
  alembic revision --autogenerate -m "create tasks table"

  # 驗證遷移腳本
  # backend/alembic/versions/xxxx_create_tasks_table.py
  # - 確認所有欄位正確
  # - 確認 Foreign Key 約束
  # - 確認 Enum 類型正確

  # 執行遷移
  alembic upgrade head

  # 驗證資料表建立
  psql -U admin -d respirally_db -c "\d development.tasks"
  ```

---

#### **Phase B2 - Task Repository Pattern 實作 [3h]**

**目標**: 實作 Repository Interface 和 Implementation

**實作 Checklist**:
- [ ] **Step 1 - Repository Interface** [1h]
  ```python
  # backend/src/respira_ally/domain/repositories/i_task_repository.py
  from abc import ABC, abstractmethod
  from typing import List, Optional
  from uuid import UUID
  from datetime import datetime

  from respira_ally.domain.entities.task import Task, TaskStatus, TaskPriority

  class ITaskRepository(ABC):
      """Task Repository Interface - 定義任務儲存庫契約"""

      @abstractmethod
      async def create(self, task: Task) -> Task:
          """創建任務"""
          pass

      @abstractmethod
      async def get_by_id(self, task_id: UUID) -> Optional[Task]:
          """根據 ID 獲取任務"""
          pass

      @abstractmethod
      async def list_by_patient(
          self,
          patient_id: UUID,
          status: Optional[TaskStatus] = None,
          priority: Optional[TaskPriority] = None,
          page: int = 0,
          page_size: int = 20
      ) -> tuple[List[Task], int]:
          """列出病患的任務（支援過濾、分頁）"""
          pass

      @abstractmethod
      async def list_by_therapist(
          self,
          therapist_id: UUID,
          status: Optional[TaskStatus] = None,
          priority: Optional[TaskPriority] = None,
          page: int = 0,
          page_size: int = 20
      ) -> tuple[List[Task], int]:
          """列出治療師的任務（支援過濾、分頁）"""
          pass

      @abstractmethod
      async def update(self, task: Task) -> Task:
          """更新任務"""
          pass

      @abstractmethod
      async def delete(self, task_id: UUID) -> bool:
          """刪除任務"""
          pass

      @abstractmethod
      async def count_by_status(
          self,
          therapist_id: UUID,
          status: TaskStatus
      ) -> int:
          """統計治療師的任務數量（按狀態）"""
          pass
  ```

- [ ] **Step 2 - Repository Implementation** [2h]
  ```python
  # backend/src/respira_ally/infrastructure/repository_impls/task_repository_impl.py
  from typing import List, Optional
  from uuid import UUID
  from sqlalchemy import select, func
  from sqlalchemy.ext.asyncio import AsyncSession

  from respira_ally.domain.repositories.i_task_repository import ITaskRepository
  from respira_ally.domain.entities.task import Task, TaskStatus, TaskPriority
  from respira_ally.infrastructure.models.task_model import TaskModel

  class TaskRepositoryImpl(ITaskRepository):
      """Task Repository Implementation - PostgreSQL 實作"""

      def __init__(self, db: AsyncSession):
          self.db = db

      def _to_entity(self, model: TaskModel) -> Task:
          """將 ORM Model 轉換為 Domain Entity"""
          return Task(
              task_id=model.task_id,
              title=model.title,
              description=model.description,
              priority=model.priority,
              status=model.status,
              patient_id=model.patient_id,
              assigned_to=model.assigned_to,
              related_alert_id=model.related_alert_id,
              created_at=model.created_at,
              updated_at=model.updated_at,
              due_date=model.due_date,
              completed_at=model.completed_at
          )

      def _to_model(self, entity: Task) -> TaskModel:
          """將 Domain Entity 轉換為 ORM Model"""
          return TaskModel(
              task_id=entity.task_id,
              title=entity.title,
              description=entity.description,
              priority=entity.priority,
              status=entity.status,
              patient_id=entity.patient_id,
              assigned_to=entity.assigned_to,
              related_alert_id=entity.related_alert_id,
              created_at=entity.created_at,
              updated_at=entity.updated_at,
              due_date=entity.due_date,
              completed_at=entity.completed_at
          )

      async def create(self, task: Task) -> Task:
          model = self._to_model(task)
          self.db.add(model)
          await self.db.commit()
          await self.db.refresh(model)
          return self._to_entity(model)

      async def get_by_id(self, task_id: UUID) -> Optional[Task]:
          result = await self.db.execute(
              select(TaskModel).where(TaskModel.task_id == task_id)
          )
          model = result.scalar_one_or_none()
          return self._to_entity(model) if model else None

      async def list_by_patient(
          self,
          patient_id: UUID,
          status: Optional[TaskStatus] = None,
          priority: Optional[TaskPriority] = None,
          page: int = 0,
          page_size: int = 20
      ) -> tuple[List[Task], int]:
          # 建立查詢
          query = select(TaskModel).where(TaskModel.patient_id == patient_id)

          # 過濾條件
          if status:
              query = query.where(TaskModel.status == status)
          if priority:
              query = query.where(TaskModel.priority == priority)

          # 排序：優先級降序 + 創建時間降序
          query = query.order_by(
              TaskModel.priority.desc(),
              TaskModel.created_at.desc()
          )

          # 計算總數
          count_query = select(func.count()).select_from(query.subquery())
          total = await self.db.scalar(count_query)

          # 分頁
          query = query.offset(page * page_size).limit(page_size)

          # 執行查詢
          result = await self.db.execute(query)
          models = result.scalars().all()

          tasks = [self._to_entity(model) for model in models]
          return tasks, total

      async def update(self, task: Task) -> Task:
          model = await self.db.get(TaskModel, task.task_id)
          if not model:
              raise ValueError(f"Task {task.task_id} not found")

          # 更新所有欄位
          model.title = task.title
          model.description = task.description
          model.priority = task.priority
          model.status = task.status
          model.assigned_to = task.assigned_to
          model.due_date = task.due_date
          model.completed_at = task.completed_at
          model.updated_at = task.updated_at

          await self.db.commit()
          await self.db.refresh(model)
          return self._to_entity(model)

      # ... 其他方法實作
  ```

---

#### **Phase B3 - Task API Endpoints 開發 [5h]**

**目標**: 實作 RESTful API 端點

**實作 Checklist**:
- [ ] **Step 1 - Pydantic Schemas** [1h]
  ```python
  # backend/src/respira_ally/api/v1/schemas/task.py
  from pydantic import BaseModel, Field
  from typing import Optional
  from datetime import datetime
  from uuid import UUID

  from respira_ally.domain.entities.task import TaskPriority, TaskStatus

  class TaskCreateRequest(BaseModel):
      title: str = Field(..., min_length=1, max_length=200)
      description: Optional[str] = None
      priority: TaskPriority = TaskPriority.MEDIUM
      patient_id: UUID
      assigned_to: Optional[UUID] = None
      related_alert_id: Optional[UUID] = None
      due_date: Optional[datetime] = None

  class TaskUpdateRequest(BaseModel):
      title: Optional[str] = Field(None, min_length=1, max_length=200)
      description: Optional[str] = None
      priority: Optional[TaskPriority] = None
      status: Optional[TaskStatus] = None
      assigned_to: Optional[UUID] = None
      due_date: Optional[datetime] = None

  class TaskResponse(BaseModel):
      task_id: UUID
      title: str
      description: Optional[str]
      priority: TaskPriority
      status: TaskStatus
      patient_id: UUID
      assigned_to: Optional[UUID]
      related_alert_id: Optional[UUID]
      created_at: datetime
      updated_at: datetime
      due_date: Optional[datetime]
      completed_at: Optional[datetime]
      is_overdue: bool

      class Config:
          from_attributes = True

  class TaskListResponse(BaseModel):
      tasks: list[TaskResponse]
      total: int
      page: int
      page_size: int
  ```

- [ ] **Step 2 - API Router** [3h]
  ```python
  # backend/src/respira_ally/api/v1/routers/task.py
  from fastapi import APIRouter, Depends, HTTPException, status, Query
  from sqlalchemy.ext.asyncio import AsyncSession
  from typing import Optional
  from uuid import UUID

  from respira_ally.api.v1.schemas.task import (
      TaskCreateRequest,
      TaskUpdateRequest,
      TaskResponse,
      TaskListResponse
  )
  from respira_ally.application.task.task_service import TaskService
  from respira_ally.infrastructure.repository_impls.task_repository_impl import TaskRepositoryImpl
  from respira_ally.infrastructure.database import get_db
  from respira_ally.domain.entities.task import TaskStatus, TaskPriority

  router = APIRouter(prefix="/tasks", tags=["Tasks"])

  def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
      repository = TaskRepositoryImpl(db)
      return TaskService(repository)

  @router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
  async def create_task(
      request: TaskCreateRequest,
      service: TaskService = Depends(get_task_service)
  ):
      """創建新任務"""
      task = await service.create_task(
          title=request.title,
          description=request.description,
          priority=request.priority,
          patient_id=request.patient_id,
          assigned_to=request.assigned_to,
          related_alert_id=request.related_alert_id,
          due_date=request.due_date
      )
      return task

  @router.get("/patients/{patient_id}/", response_model=TaskListResponse)
  async def list_patient_tasks(
      patient_id: UUID,
      task_status: Optional[TaskStatus] = Query(None, alias="status"),
      priority: Optional[TaskPriority] = None,
      page: int = Query(0, ge=0),
      page_size: int = Query(20, ge=1, le=100),
      service: TaskService = Depends(get_task_service)
  ):
      """列出病患的任務"""
      tasks, total = await service.list_patient_tasks(
          patient_id=patient_id,
          status=task_status,
          priority=priority,
          page=page,
          page_size=page_size
      )

      return TaskListResponse(
          tasks=[TaskResponse.from_orm(task) for task in tasks],
          total=total,
          page=page,
          page_size=page_size
      )

  @router.patch("/{task_id}", response_model=TaskResponse)
  async def update_task(
      task_id: UUID,
      request: TaskUpdateRequest,
      service: TaskService = Depends(get_task_service)
  ):
      """更新任務"""
      task = await service.update_task(
          task_id=task_id,
          **request.dict(exclude_unset=True)
      )
      if not task:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail=f"Task {task_id} not found"
          )
      return task

  @router.post("/{task_id}/start", response_model=TaskResponse)
  async def start_task(
      task_id: UUID,
      service: TaskService = Depends(get_task_service)
  ):
      """開始執行任務"""
      task = await service.start_task(task_id)
      return task

  @router.post("/{task_id}/complete", response_model=TaskResponse)
  async def complete_task(
      task_id: UUID,
      service: TaskService = Depends(get_task_service)
  ):
      """完成任務"""
      task = await service.complete_task(task_id)
      return task
  ```

- [ ] **Step 3 - Task Service** [1h]
  ```python
  # backend/src/respira_ally/application/task/task_service.py
  from typing import Optional, List
  from uuid import UUID, uuid4
  from datetime import datetime

  from respira_ally.domain.repositories.i_task_repository import ITaskRepository
  from respira_ally.domain.entities.task import Task, TaskStatus, TaskPriority

  class TaskService:
      """Task Application Service - 任務管理業務邏輯"""

      def __init__(self, repository: ITaskRepository):
          self.repository = repository

      async def create_task(
          self,
          title: str,
          patient_id: UUID,
          priority: TaskPriority = TaskPriority.MEDIUM,
          description: Optional[str] = None,
          assigned_to: Optional[UUID] = None,
          related_alert_id: Optional[UUID] = None,
          due_date: Optional[datetime] = None
      ) -> Task:
          """創建新任務"""
          task = Task(
              task_id=uuid4(),
              title=title,
              description=description,
              priority=priority,
              status=TaskStatus.TODO,
              patient_id=patient_id,
              assigned_to=assigned_to,
              related_alert_id=related_alert_id,
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              due_date=due_date,
              completed_at=None
          )

          return await self.repository.create(task)

      async def start_task(self, task_id: UUID) -> Task:
          """開始執行任務"""
          task = await self.repository.get_by_id(task_id)
          if not task:
              raise ValueError(f"Task {task_id} not found")

          task.start()
          return await self.repository.update(task)

      async def complete_task(self, task_id: UUID) -> Task:
          """完成任務"""
          task = await self.repository.get_by_id(task_id)
          if not task:
              raise ValueError(f"Task {task_id} not found")

          task.complete()
          return await self.repository.update(task)

      # ... 其他業務方法
  ```

---

#### **Phase B4 - 自動任務生成邏輯 [8h]**

**目標**: 實作 Alert → Task 自動創建邏輯

**實作 Checklist**:
- [ ] **Step 1 - Task Priority Calculator** [2h]
  ```python
  # backend/src/respira_ally/domain/services/task_priority_calculator.py
  from respira_ally.domain.entities.task import TaskPriority
  from respira_ally.domain.entities.alert import AlertSeverity
  from respira_ally.infrastructure.models.risk_assessment_model import GoldGroup

  class TaskPriorityCalculator:
      """任務優先級計算器 - 基於 GOLD ABE + Alert Severity"""

      @staticmethod
      def calculate_from_alert(
          alert_severity: AlertSeverity,
          gold_group: GoldGroup
      ) -> TaskPriority:
          """
          根據 Alert Severity 和 GOLD ABE 分級計算任務優先級

          規則:
          1. CRITICAL Alert + GOLD E → CRITICAL Task
          2. HIGH Alert + GOLD E → CRITICAL Task
          3. HIGH Alert + GOLD B → HIGH Task
          4. MEDIUM Alert → MEDIUM Task
          5. LOW Alert → LOW Task
          """

          # CRITICAL Alert 永遠產生 CRITICAL Task
          if alert_severity == AlertSeverity.CRITICAL:
              return TaskPriority.CRITICAL

          # GOLD E 患者的 HIGH Alert → CRITICAL Task
          if alert_severity == AlertSeverity.HIGH and gold_group == GoldGroup.E:
              return TaskPriority.CRITICAL

          # GOLD B 患者的 HIGH Alert → HIGH Task
          if alert_severity == AlertSeverity.HIGH and gold_group == GoldGroup.B:
              return TaskPriority.HIGH

          # 其他情況直接映射
          severity_to_priority = {
              AlertSeverity.HIGH: TaskPriority.HIGH,
              AlertSeverity.MEDIUM: TaskPriority.MEDIUM,
              AlertSeverity.LOW: TaskPriority.LOW
          }

          return severity_to_priority.get(alert_severity, TaskPriority.MEDIUM)
  ```

- [ ] **Step 2 - Auto Task Generation Use Case** [4h]
  ```python
  # backend/src/respira_ally/application/task/use_cases/auto_generate_task_use_case.py
  from uuid import UUID
  from datetime import datetime, timedelta
  from typing import Optional

  from respira_ally.domain.repositories.i_task_repository import ITaskRepository
  from respira_ally.domain.repositories.i_alert_repository import IAlertRepository
  from respira_ally.domain.repositories.i_patient_repository import IPatientRepository
  from respira_ally.domain.services.task_priority_calculator import TaskPriorityCalculator
  from respira_ally.domain.entities.task import Task, TaskStatus
  from respira_ally.domain.entities.alert import AlertType

  class AutoGenerateTaskUseCase:
      """自動任務生成 Use Case - 當 Alert 觸發時自動創建 Task"""

      def __init__(
          self,
          task_repo: ITaskRepository,
          alert_repo: IAlertRepository,
          patient_repo: IPatientRepository
      ):
          self.task_repo = task_repo
          self.alert_repo = alert_repo
          self.patient_repo = patient_repo

      async def execute(self, alert_id: UUID) -> Task:
          """
          根據 Alert 自動生成對應的 Task

          流程:
          1. 獲取 Alert 詳情
          2. 獲取病患的 GOLD ABE 分級
          3. 計算任務優先級
          4. 自動分配給病患的主治療師
          5. 創建任務
          """

          # 1. 獲取 Alert
          alert = await self.alert_repo.get_by_id(alert_id)
          if not alert:
              raise ValueError(f"Alert {alert_id} not found")

          # 2. 獲取病患資料（包含 therapist_id 和 GOLD ABE）
          patient = await self.patient_repo.get_by_id(alert.patient_id)
          if not patient:
              raise ValueError(f"Patient {alert.patient_id} not found")

          # 3. 計算任務優先級
          priority = TaskPriorityCalculator.calculate_from_alert(
              alert_severity=alert.severity,
              gold_group=patient.gold_group  # 從最新 RiskAssessment 取得
          )

          # 4. 根據 Alert 類型生成任務標題和描述
          title, description = self._generate_task_content(alert)

          # 5. 設定截止日期（根據優先級）
          due_date = self._calculate_due_date(priority)

          # 6. 創建任務
          task = Task(
              task_id=uuid4(),
              title=title,
              description=description,
              priority=priority,
              status=TaskStatus.TODO,
              patient_id=alert.patient_id,
              assigned_to=patient.therapist_id,  # 自動分配給主治療師
              related_alert_id=alert_id,
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              due_date=due_date,
              completed_at=None
          )

          return await self.task_repo.create(task)

      def _generate_task_content(self, alert) -> tuple[str, str]:
          """根據 Alert 類型生成任務內容"""

          templates = {
              AlertType.GOLD_GROUP_E: (
                  "🚨 高風險病患需立即評估",
                  f"病患被評估為 GOLD Group E（最高風險），"
                  f"需要立即進行臨床評估並制定密集監護計畫。"
                  f"過去 12 個月內有多次惡化或住院記錄。"
              ),
              AlertType.HIGH_CAT_SCORE: (
                  "⚠️ 嚴重症狀負擔需關注",
                  f"病患 CAT 分數 >= 20，顯示嚴重的症狀負擔。"
                  f"建議評估當前治療計畫的有效性，考慮調整用藥或增加復健頻率。"
              ),
              AlertType.FREQUENT_EXACERBATIONS: (
                  "📊 頻繁惡化需介入",
                  f"病患過去 12 個月內有 >= 3 次惡化事件。"
                  f"建議檢討預防性治療策略，加強病患自我管理教育。"
              )
          }

          return templates.get(
              alert.alert_type,
              ("需要處理的 Alert", f"Alert ID: {alert.alert_id}")
          )

      def _calculate_due_date(self, priority: TaskPriority) -> datetime:
          """根據優先級計算截止日期"""

          now = datetime.utcnow()

          due_date_mapping = {
              TaskPriority.CRITICAL: now + timedelta(hours=24),   # 24 小時內
              TaskPriority.HIGH: now + timedelta(days=3),         # 3 天內
              TaskPriority.MEDIUM: now + timedelta(days=7),       # 7 天內
              TaskPriority.LOW: now + timedelta(days=14)          # 14 天內
          }

          return due_date_mapping.get(priority, now + timedelta(days=7))
  ```

- [ ] **Step 3 - 整合到 CalculateRiskUseCase** [2h]
  ```python
  # 修改 backend/src/respira_ally/application/risk/use_cases/calculate_risk_use_case.py

  # 在 execute() 方法的 Alert 創建後，添加：

  # 自動生成 Task（如果 Alert 是 CRITICAL 或 HIGH）
  if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
      auto_task_use_case = AutoGenerateTaskUseCase(
          task_repo=task_repo,  # 需要注入
          alert_repo=alert_repo,
          patient_repo=patient_repo
      )

      task = await auto_task_use_case.execute(alert.alert_id)
      logger.info(f"Auto-generated Task {task.task_id} for Alert {alert.alert_id}")
  ```

---

#### **Phase B5 - 任務分配邏輯與測試 [4h]**

**實作 Checklist**:
- [ ] **Step 1 - Task Assignment Service** [2h]
  ```python
  # backend/src/respira_ally/domain/services/task_assignment_service.py
  from uuid import UUID
  from typing import Optional

  from respira_ally.domain.repositories.i_task_repository import ITaskRepository
  from respira_ally.domain.repositories.i_patient_repository import IPatientRepository

  class TaskAssignmentService:
      """任務分配服務 - 負責任務分配邏輯"""

      def __init__(
          self,
          task_repo: ITaskRepository,
          patient_repo: IPatientRepository
      ):
          self.task_repo = task_repo
          self.patient_repo = patient_repo

      async def auto_assign_to_primary_therapist(self, task_id: UUID) -> bool:
          """自動分配給病患的主治療師"""

          task = await self.task_repo.get_by_id(task_id)
          if not task:
              raise ValueError(f"Task {task_id} not found")

          # 獲取病患資料
          patient = await self.patient_repo.get_by_id(task.patient_id)
          if not patient or not patient.therapist_id:
              return False

          # 分配任務
          task.assign_to(patient.therapist_id)
          await self.task_repo.update(task)

          return True

      async def reassign_task(
          self,
          task_id: UUID,
          new_therapist_id: UUID
      ) -> bool:
          """手動重新分配任務"""

          task = await self.task_repo.get_by_id(task_id)
          if not task:
              raise ValueError(f"Task {task_id} not found")

          task.assign_to(new_therapist_id)
          await self.task_repo.update(task)

          return True
  ```

- [ ] **Step 2 - 整合測試** [2h]
  ```python
  # backend/tests/integration/test_task_management.py
  import pytest
  from uuid import uuid4

  @pytest.mark.asyncio
  async def test_auto_task_generation_from_alert():
      """測試：Alert 觸發後自動創建 Task"""

      # 1. 創建測試病患
      patient_id = uuid4()

      # 2. 觸發風險評估（會創建 Alert）
      # ...

      # 3. 驗證 Task 自動創建
      tasks = await task_service.list_patient_tasks(patient_id)
      assert len(tasks) == 1
      assert tasks[0].related_alert_id is not None

  @pytest.mark.asyncio
  async def test_task_priority_calculation():
      """測試：任務優先級計算"""

      # CRITICAL Alert + GOLD E → CRITICAL Task
      priority = TaskPriorityCalculator.calculate_from_alert(
          alert_severity=AlertSeverity.CRITICAL,
          gold_group=GoldGroup.E
      )
      assert priority == TaskPriority.CRITICAL
  ```

---

#### **Role B - Git Workflow**

**每日提交規範**:
```bash
# Day 1 結束
git add .
git commit -m "feat(backend): implement Task Entity and Repository Pattern

- Add Task domain entity with status transitions
- Add TaskModel (SQLAlchemy) with database schema
- Add ITaskRepository interface
- Add TaskRepositoryImpl with CRUD operations
- Create Alembic migration for tasks table

Follows DDD architecture with clean separation of concerns"

git push origin feature/task-management

# Day 2 結束
git add .
git commit -m "feat(backend): implement Task Management API

- Add Task API endpoints (CRUD + status transitions)
- Add TaskService for business logic
- Add Pydantic schemas for validation
- Add auto task generation from alerts
- Add TaskPriorityCalculator

Task Management backend is now feature-complete"

git push origin feature/task-management
```

---

## 🔄 整合階段 - Task Board UI [4h]

**由 Role A 執行，依賴 Role B 完成 Task API**

**實作 Checklist**:
- [ ] **TaskBoard Component** [2h]
  - [ ] 使用 react-beautiful-dnd 實作拖拽
  - [ ] 3 欄布局：TODO | IN_PROGRESS | DONE
  - [ ] 拖拽更新任務狀態

- [ ] **TaskDetail Modal** [1h]
  - [ ] 顯示任務詳情
  - [ ] 支援手動狀態更新
  - [ ] 顯示關聯的 Alert

- [ ] **整合測試** [1h]
  - [ ] 測試拖拽功能
  - [ ] 測試狀態更新 API 調用
  - [ ] 測試 Task 列表刷新

---

## 🧪 E2E 測試與驗證 [2h]

**由 Role A + Role B 共同執行**

**測試場景**:
1. **Alert → Task 自動創建流程**
   - [ ] 觸發風險評估 → 創建 CRITICAL Alert
   - [ ] 驗證 Task 自動創建
   - [ ] 驗證任務優先級正確
   - [ ] 驗證自動分配給治療師

2. **Task 完整生命週期**
   - [ ] 創建 Task (手動 + 自動)
   - [ ] 分配 Task
   - [ ] 開始 Task (TODO → IN_PROGRESS)
   - [ ] 完成 Task (IN_PROGRESS → DONE)

3. **UI 整合驗證**
   - [ ] Alert List 顯示正確
   - [ ] Alert Badge 數量正確
   - [ ] Task Board 拖拽功能正常
   - [ ] 所有過濾和分頁功能正常

---

## 🚧 衝突預防與溝通機制

### Git 分支策略

```
dev (main branch)
├── feature/alert-ui (Role A)
│   ├── feat: Alert List Component
│   ├── feat: Alert Detail Modal
│   ├── feat: Alert Badge
│   └── merge → dev (Day 2 end)
│
└── feature/task-management (Role B)
    ├── feat: Task Entity + Repository
    ├── feat: Task API
    ├── feat: Auto Task Generation
    └── merge → dev (Day 4 end)
```

### 每日同步機制

**每日 Standup (15 分鐘)**:
- Role A: 昨天完成了什麼？今天計劃做什麼？有沒有阻礙？
- Role B: 昨天完成了什麼？今天計劃做什麼？有沒有阻礙？

**每日整合 (Day 2 & Day 3)**:
```bash
# Role A 完成 Alert UI 後 (Day 2)
git checkout dev
git pull origin dev
git merge feature/alert-ui
git push origin dev

# Role B 持續開發 Task Management
git checkout feature/task-management
git rebase dev  # 保持分支最新
```

### API 契約協調

**API 契約文件**: `docs/06_api_design_specification.md`

Role A 和 Role B 在開發前必須共同確認：
1. Task API 端點定義
2. Request/Response Schema
3. 錯誤碼定義
4. 分頁、過濾、排序參數

---

## 📊 進度追蹤表

### Role A - Alert UI 進度

| 任務 | 預估 | 實際 | 狀態 | 負責人 |
|------|------|------|------|--------|
| A1 - Alert List Component | 3h | - | ⏳ | Role A |
| A2 - Alert Detail Modal | 2h | - | ⏳ | Role A |
| A3 - Dashboard Alert Badge | 2h | - | ⏳ | Role A |
| A4 - API Integration Test | 1h | - | ⏳ | Role A |
| **小計** | **8h** | - | - | - |

### Role B - Task Management 進度

| 任務 | 預估 | 實際 | 狀態 | 負責人 |
|------|------|------|------|--------|
| B1 - Task Entity 設計 | 4h | - | ⏳ | Role B |
| B2 - Repository Pattern | 3h | - | ⏳ | Role B |
| B3 - Task API 開發 | 5h | - | ⏳ | Role B |
| B4 - 自動任務生成 | 8h | - | ⏳ | Role B |
| B5 - 任務分配邏輯 | 4h | - | ⏳ | Role B |
| **小計** | **24h** | - | - | - |

### 整合與測試進度

| 任務 | 預估 | 實際 | 狀態 | 負責人 |
|------|------|------|------|--------|
| Task Board UI | 4h | - | ⏳ | Role A (依賴 B) |
| E2E Testing | 2h | - | ⏳ | A + B |
| **總計** | **38h** | - | - | - |

**並行執行後實際時程**: 24-28 小時（縮短約 10 小時）

---

## 🎯 驗收標準

### Phase 1 - Alert UI (Role A)
- [ ] ✅ Alert List 顯示所有 Alert，支援過濾（Severity, Status）
- [ ] ✅ Alert Detail Modal 顯示完整 metadata
- [ ] ✅ Dashboard Alert Badge 顯示正確的活動 Alert 數量
- [ ] ✅ 所有 API 調用成功，錯誤處理完善

### Phase 2 - Task Management (Role B)
- [ ] ✅ Task Entity 遵循 DDD 設計，業務邏輯封裝在 Entity
- [ ] ✅ Repository Pattern 完整實作，支援 CRUD + 過濾
- [ ] ✅ Task API 端點完整，支援創建、列表、更新、狀態轉換
- [ ] ✅ Alert → Task 自動創建功能正常運作
- [ ] ✅ 任務優先級計算正確（基於 GOLD ABE + Alert Severity）

### Phase 3 - 整合驗證
- [ ] ✅ Task Board UI 拖拽功能正常
- [ ] ✅ E2E 測試通過（Alert → Task → Therapist Action）
- [ ] ✅ 無 Git 衝突，代碼整合順利

---

## 🚀 開始執行

**立即行動步驟**:

1. **建立分支**:
   ```bash
   # Role A
   git checkout dev
   git pull origin dev
   git checkout -b feature/alert-ui

   # Role B
   git checkout dev
   git pull origin dev
   git checkout -b feature/task-management
   ```

2. **確認環境**:
   - Role A: `npm run dev` 確認前端可啟動
   - Role B: `alembic upgrade head` 確認資料庫最新

3. **開始開發**:
   - Role A: 從 A1 - Alert List Component 開始
   - Role B: 從 B1 - Task Entity 設計開始

4. **每日整合**:
   - Day 2 End: Role A merge feature/alert-ui → dev
   - Day 4 End: Role B merge feature/task-management → dev

---

## 📚 參考資源

- **DDD 架構**: `docs/03_architecture_and_design_document.md`
- **API 設計**: `docs/06_api_design_specification.md`
- **Alert System**: `docs/dev_logs/CHANGELOG_20251026.md`
- **Git 工作流程**: `CLAUDE.md` - Git Workflow 章節

---

**文件維護者**: TaskMaster Hub
**最後更新**: 2025-10-27
**版本**: v1.0
