# 架構決策紀錄 (ADR) 總覽

本目錄存放 `RespiraAlly` 專案所有重要的架構決策紀錄 (Architecture Decision Records, ADRs)。

每個 ADR 檔案都旨在記錄一個重要的架構決策、其背景、考量的方案、以及決策的後果。這有助於團隊成員（特別是新成員）理解系統為何是現在的樣子，並確保未來決策的一致性。

## ADR 索引

| ADR ID | 決策 | 狀態 |
| :--- | :--- | :--- |
| **[ADR-001](./ADR-001-fastapi-vs-flask.md)** | 採用 FastAPI 作為後端框架，而非延續使用 Flask | 已決定 |
| **[ADR-002](./ADR-002-pgvector-for-vector-db.md)** | 採用 pgvector 作為初期的向量資料庫方案 | 已決定 |
| **[ADR-003](./ADR-003-mongodb-for-event-logs.md)** | 採用 MongoDB 儲存事件與非結構化日誌 | 已決定 |
| **[ADR-004](./ADR-004-line-as-patient-entrypoint.md)** | 採用 LINE 作為唯一的病患互動入口 | 已決定 |
| **[ADR-005](./ADR-005-rabbitmq-for-message-queue.md)** | 採用 RabbitMQ 作為異步任務的訊息佇列 | 已決定 |
| **[ADR-006](./ADR-006-smart-reminders-schedule.md)** | 採用三時段 (12:00/17:00/20:00) 智慧提醒策略 | 已決定 |
| **[ADR-007](./ADR-007-persona-based-messaging-tone.md)** | 採用擬人化（孫女）口吻設計提醒訊息 | 已決定 |

## 如何建立新的 ADR

1.  複製 `VibeCoding_Workflow_Templates/04_architecture_decision_record_template.md` 範本。
2.  將檔案命名為 `ADR-XXX-short-description.md`，其中 `XXX` 是下一個序列號。
3.  填寫 ADR 內容。
4.  提交 PR 進行團隊審核。
