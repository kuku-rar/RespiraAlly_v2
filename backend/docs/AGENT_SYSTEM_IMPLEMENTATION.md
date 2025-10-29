# Agent System Implementation - Sprint 6 LLM + RAG

**實作日期**: 2025-10-29
**狀態**: ✅ Phase 1 完成 - Agents 與 RAG 工具已實作
**參考架構**: beloved_grandson/services/ai-worker/worker/llm_app

---

## 📋 實作概要

基於 beloved_grandson 的設計模式，實作 COPD 專用的 AI Agent 系統，包含：
- ✅ Guardrail Agent（安全檢查）
- ✅ Health Agent（健康照護 + RAG）
- ✅ AgentManager（協調器）
- ✅ GuardrailTool（安全檢查工具）
- ✅ COPDKnowledgeTool（RAG 工具）

---

## 🏗️ 架構設計

### 核心原則

遵循 beloved_grandson 的關鍵設計決策：
- **memory=False**: 不使用 CrewAI 內建 ChromaDB 記憶
- **Repository Pattern**: 使用 DDD 的 Repository 介面分離關注點
- **兩階段處理**: Guardrail 檢查 → Health Agent 回覆
- **Fallback 機制**: CrewAI 失敗時降級為 OpenAI + RAG

### 目錄結構

```
backend/src/respira_ally/
├── agents/
│   ├── __init__.py
│   ├── guardrail_agent.py      # Guardrail Agent 創建函數
│   └── health_agent.py          # Health Agent 創建函數
├── tools/
│   ├── __init__.py
│   ├── guardrail_tool.py        # COPD 安全檢查工具
│   └── rag_tool.py               # pgvector RAG 工具
├── services/
│   └── agent_manager.py          # Agent 管理器與協調邏輯
├── domain/
│   ├── repositories/
│   │   ├── conversation_repository.py  # 對話歷史介面
│   │   └── knowledge_repository.py     # 知識庫介面
│   └── value_objects/
│       ├── conversation.py             # Message 值對象
│       └── knowledge.py                 # Document 值對象
└── infrastructure/
    └── repository_impls/
        ├── redis_conversation_repository.py    # Redis 實現
        └── pgvector_knowledge_repository.py     # pgvector 實現
```

---

## 🛠️ 元件詳細設計

### 1. GuardrailTool

**檔案**: `src/respira_ally/tools/guardrail_tool.py`

**職責**: 使用 OpenAI 判斷用戶輸入是否安全

**輸入**: 用戶文本

**輸出**:
- `"OK"` - 安全，可處理
- `"BLOCK: <原因>"` - 需要攔截

**特點**:
- Temperature = 0（確保一致性）
- 使用 gpt-4o-mini
- fail-open 策略（錯誤時預設為安全）

**安全檢查規則**:
- ✅ 允許：症狀描述、衛教詢問、情緒表達
- ❌ 攔截：違法內容、成人內容、具體醫療指導、自殺方法指導

---

### 2. COPDKnowledgeTool

**檔案**: `src/respira_ally/tools/rag_tool.py`

**職責**: 從 pgvector 知識庫檢索相關 COPD 知識

**輸入**:
- query (str): 用戶查詢
- top_k (int): 返回前 K 個最相關文檔（預設 3）

**輸出**: 格式化的檢索結果（含相似度、類別、關鍵詞、注意事項）

**特點**:
- 異步執行（使用 asyncio.run）
- 語義搜索（OpenAI embeddings + pgvector cosine similarity）
- 友好的錯誤處理與降級提示

**RAG 流程**:
1. 用戶查詢 → OpenAI embedding（1536 維）
2. pgvector cosine similarity 搜索
3. 返回前 K 個最相關 Q&A
4. 格式化為可讀文本

---

### 3. Guardrail Agent

**檔案**: `src/respira_ally/agents/guardrail_agent.py`

**職責**: 安全檢查代理

**配置**:
- Role: "COPD Safety Guardrail"
- LLM: gpt-4o-mini, temperature=0
- Tools: [GuardrailTool]
- memory: False
- allow_delegation: False

**工作方式**:
```python
guard_task = Task(
    description="只判斷此輸入是否需要『攔截』：...",
    expected_output="OK 或 BLOCK: <原因>",
    agent=guardrail_agent
)
result = Crew(agents=[guard], tasks=[guard_task]).kickoff().raw
```

---

### 4. Health Agent

**檔案**: `src/respira_ally/agents/health_agent.py`

**職責**: COPD 健康照護助手（含 RAG）

**配置**:
- Role: "COPD Care Companion"
- LLM: gpt-4o-mini, temperature=0.7（自然對話）
- Tools: [COPDKnowledgeTool]
- memory: False
- allow_delegation: False
- max_iterations: 3（限制工具調用次數）

**回覆策略**:
- 需要客觀知識 → 先調用 COPDKnowledgeTool
- 理解檢索結果重點
- 用自己的話回覆（保持對話自然性）
- 必要時提醒就醫

---

### 5. AgentManager

**檔案**: `src/respira_ally/services/agent_manager.py`

**職責**: 協調 Guardrail 和 Health Agent 的執行

**核心方法**:

```python
async def handle_message(
    user_id: UUID | str,
    user_input: str,
    include_context: bool = True
) -> str:
    """
    兩階段處理流程：
    1. Guardrail 安全檢查
    2. 如果通過 → Health Agent 回覆
       如果攔截 → 婉拒訊息
    """
```

**Agent 管理**:
- **Guardrail Agent**: 單例（所有用戶共用）
- **Health Agent**: 按 user_id 緩存

**上下文管理**:
- 可選地從 ConversationRepository 獲取最近 6 輪對話
- 提供給 Health Agent 作為上下文

**Fallback 機制**:
- CrewAI 失敗 → OpenAI + RAG 工具直接調用
- 確保服務可用性

---

## 🧪 測試

**測試腳本**: `scripts/test_agents.py`

**測試案例**:

1. **正常 COPD 症狀詢問**
   - 輸入: "我最近常常喘不過氣，COPD 患者應該怎麼運動？"
   - 預期: 通過安全檢查 + RAG 檢索 + 實用建議

2. **不當醫療指導請求**
   - 輸入: "我應該吃多少毫克的類固醇？請幫我開藥。"
   - 預期: Guardrail 攔截 + 婉拒訊息

3. **一般健康諮詢**
   - 輸入: "COPD 患者可以吃什麼食物比較好？"
   - 預期: RAG 檢索 + 飲食建議

4. **緊急症狀**
   - 輸入: "我現在呼吸很困難，嘴唇發紫，該怎麼辦？"
   - 預期: 立即建議撥打 119 或前往急診

**執行測試**:
```bash
cd backend
uv run python scripts/test_agents.py
```

---

## 🔧 依賴項

### Python 套件（已安裝）

```toml
crewai = "0.28.0"
pandas = "2.3.3"
openpyxl = "3.1.5"
setuptools = "80.9.0"
```

### 環境變數（需設定）

```bash
# .env 檔案
OPENAI_API_KEY=sk-...              # OpenAI API 金鑰
MODEL_NAME=gpt-4o-mini              # 預設模型
OTEL_SDK_DISABLED=true              # 禁用遙測
CREWAI_TELEMETRY_OPT_OUT=true      # 禁用 CrewAI 遙測
```

---

## 🚀 使用方式

### 基本用法

```python
from respira_ally.services.agent_manager import AgentManager

# 初始化 Manager
manager = AgentManager()

# 處理用戶訊息
response = await manager.handle_message(
    user_id="patient-123",
    user_input="COPD 患者可以做什麼運動？",
    include_context=True  # 包含對話歷史
)

print(response)
```

### 整合 Repository

```python
from respira_ally.infrastructure.database.session import AsyncSessionLocal
from respira_ally.infrastructure.repository_impls.redis_conversation_repository import RedisConversationRepository
from respira_ally.infrastructure.repository_impls.pgvector_knowledge_repository import PgvectorKnowledgeRepository
from redis.asyncio import Redis

# 初始化 repositories
async with AsyncSessionLocal() as db_session:
    redis_client = Redis(host='localhost', port=6379)

    conversation_repo = RedisConversationRepository(redis_client, ttl=300)
    knowledge_repo = PgvectorKnowledgeRepository(db_session)

    manager = AgentManager(
        conversation_repo=conversation_repo,
        knowledge_repo=knowledge_repo
    )

    response = await manager.handle_message(...)
```

---

## 📊 性能考量

### Token 使用量估算

**單次對話**:
- Guardrail 檢查: ~100-200 tokens
- RAG 檢索: ~1000-1500 tokens（含檢索結果）
- Health Agent 回覆: ~200-500 tokens
- **總計**: ~1300-2200 tokens/對話

**成本估算** (gpt-4o-mini):
- 輸入: $0.15 / 1M tokens
- 輸出: $0.60 / 1M tokens
- **每對話成本**: ~$0.0003-0.0005 USD

### 響應時間

- Guardrail 檢查: ~1-2 秒
- RAG 檢索: ~2-3 秒
- Health Agent 回覆: ~2-4 秒
- **總計**: ~5-9 秒/對話

---

## 🔄 下一步（Sprint 6 Phase 2）

### 待完成任務

1. **載入實際 COPD 知識庫**
   - 設定 OPENAI_API_KEY
   - 執行 `scripts/load_copd_knowledge.py`
   - 載入 153 條 COPD Q&A（含 embeddings）

2. **實作 LINE Webhook → RabbitMQ**
   - LINE Bot 接收訊息
   - 發布到 RabbitMQ
   - 返回 200 OK

3. **實作 RabbitMQ Consumer**
   - 從 Queue 取得訊息
   - 調用 AgentManager
   - 回覆到 LINE

4. **端到端測試**
   - LINE → Webhook → RabbitMQ → Agent → Response
   - 驗證完整流程

### 可選增強

- [ ] AlertCaseManagerTool（緊急通報）
- [ ] MemoryGateTool（記憶檢索決策）
- [ ] 對話歷史摘要（降低 token 成本）
- [ ] 多輪對話上下文管理

---

## 📚 參考資料

- **beloved_grandson 架構**: `/mnt/a/AIPE01_期末專題/beloved_grandson/services/ai-worker/worker/llm_app/`
- **CrewAI 文檔**: https://docs.crewai.com/
- **pgvector 文檔**: https://github.com/pgvector/pgvector
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings

---

**實作者**: Claude Code
**審核者**: [待填]
**版本**: v1.0
**最後更新**: 2025-10-29
