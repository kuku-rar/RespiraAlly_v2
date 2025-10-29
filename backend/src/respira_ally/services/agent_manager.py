"""
Agent Manager - Crew Coordination for COPD Care

管理 Guardrail Agent 和 Health Agent 的協調執行
遵循 beloved_grandson 的兩階段處理模式：Guardrail → Health
"""

import os
from typing import Optional
from uuid import UUID

# 禁用 CrewAI 遙測功能（避免連接錯誤）
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

from crewai import Agent, Crew, Task
from openai import OpenAI

from respira_ally.agents import create_guardrail_agent, create_health_agent
from respira_ally.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from respira_ally.domain.repositories.knowledge_repository import KnowledgeRepository
from respira_ally.tools import COPDKnowledgeTool, GuardrailTool


class AgentManager:
    """
    Agent 管理器

    職責：
    1. 管理 Guardrail Agent（單例）和 Health Agent（按 user_id 緩存）
    2. 協調兩階段處理流程：Guardrail 檢查 → Health Agent 回覆
    3. 提供 fallback 機制（CrewAI 失敗時使用 OpenAI）
    """

    def __init__(
        self,
        conversation_repo: Optional[ConversationRepository] = None,
        knowledge_repo: Optional[KnowledgeRepository] = None,
    ):
        """
        初始化 Agent Manager

        Args:
            conversation_repo: 對話歷史存儲（用於上下文）
            knowledge_repo: 知識庫存儲（用於 RAG）
        """
        # 單例 Guardrail Agent（所有用戶共用）
        self.guardrail_agent = create_guardrail_agent()

        # Health Agent 緩存（按 user_id）
        self.health_agent_cache: dict[str, Agent] = {}

        # Repository 注入
        self.conversation_repo = conversation_repo
        self.knowledge_repo = knowledge_repo

    def get_guardrail(self) -> Agent:
        """獲取 Guardrail Agent（單例）"""
        return self.guardrail_agent

    def get_health_agent(self, user_id: UUID | str) -> Agent:
        """
        獲取 Health Agent（按 user_id 緩存）

        Args:
            user_id: 用戶 ID

        Returns:
            Health Agent 實例
        """
        user_id_str = str(user_id)

        if user_id_str not in self.health_agent_cache:
            self.health_agent_cache[user_id_str] = create_health_agent(user_id)

        return self.health_agent_cache[user_id_str]

    def release_health_agent(self, user_id: UUID | str) -> None:
        """
        釋放 Health Agent（清除緩存）

        Args:
            user_id: 用戶 ID
        """
        user_id_str = str(user_id)
        if user_id_str in self.health_agent_cache:
            del self.health_agent_cache[user_id_str]

    async def handle_message(
        self,
        user_id: UUID | str,
        user_input: str,
        include_context: bool = True,
    ) -> str:
        """
        處理用戶訊息（兩階段流程）

        流程：
        1. Guardrail Agent 檢查安全性
        2. 如果通過，Health Agent 提供回覆
        3. 如果攔截，返回婉拒訊息

        Args:
            user_id: 用戶 ID
            user_input: 用戶輸入
            include_context: 是否包含對話歷史上下文

        Returns:
            AI 回覆內容
        """
        # ========== 階段 1: Guardrail 檢查 ==========
        try:
            guard = self.get_guardrail()
            guard_task = Task(
                description=(
                    f"只判斷此輸入是否需要『攔截』：『{user_input}』。\n"
                    "務必使用 copd_guardrail_check 工具進行判斷；"
                    "僅輸出 OK 或 BLOCK: <原因>，不得回答內容本身。"
                ),
                expected_output="OK 或 BLOCK: <原因>",
                agent=guard,
            )

            guard_result = (
                Crew(agents=[guard], tasks=[guard_task], verbose=False).kickoff().raw
                or ""
            ).strip()

            print(f"🛡️ Guardrail 檢查: {guard_result}")

        except Exception as e:
            print(f"[Guardrail Error] {e}")
            # Fallback: 直接調用工具
            guard_result = GuardrailTool()._run(user_input)

        # 判斷是否攔截
        is_blocked = guard_result.startswith("BLOCK:")
        block_reason = guard_result[6:].strip() if is_blocked else ""

        # ========== 階段 2: Health Agent 回覆 ==========
        # 構建上下文（如果需要）
        context = ""
        if include_context and self.conversation_repo:
            try:
                # 獲取最近 6 輪對話
                messages = await self.conversation_repo.get_history(user_id, limit=6)
                if messages:
                    context_parts = ["📝 最近對話：\n"]
                    for msg in messages:
                        role_emoji = "👤" if msg.role.value == "user" else "🤖"
                        context_parts.append(f"{role_emoji} {msg.content}")
                    context = "\n".join(context_parts) + "\n\n"
            except Exception as e:
                print(f"[Context Error] {e}")

        # 如果被攔截，返回婉拒訊息
        if is_blocked:
            return await self._generate_blocked_response(
                user_id, user_input, block_reason, context
            )

        # 如果通過檢查，使用 Health Agent 生成回覆
        return await self._generate_health_response(user_id, user_input, context)

    async def _generate_blocked_response(
        self, user_id: UUID | str, user_input: str, reason: str, context: str
    ) -> str:
        """
        生成攔截時的婉拒訊息

        Args:
            user_id: 用戶 ID
            user_input: 用戶輸入
            reason: 攔截原因
            context: 對話上下文

        Returns:
            婉拒訊息
        """
        try:
            care = self.get_health_agent(user_id)

            task = Task(
                description=(
                    f"{context}"
                    f"使用者輸入：{user_input}\n\n"
                    f"【安全政策—必須婉拒】\n"
                    f"此輸入被判定為超出能力範圍（{reason}）。\n"
                    "請用溫暖的口吻婉拒，說明無法提供具體建議，"
                    "並建議用戶尋求專業醫療人員協助。\n"
                    "回覆不超過 50 字，語氣親切關心。\n"
                    "嚴禁呼叫任何工具。"
                ),
                expected_output="溫暖的婉拒訊息（50字內）",
                agent=care,
            )

            response = (
                Crew(agents=[care], tasks=[task], verbose=False).kickoff().raw or ""
            ).strip()

            return response or "很抱歉，這個問題超出我的能力範圍，建議您諮詢專業醫療人員喔。"

        except Exception as e:
            print(f"[Blocked Response Error] {e}")
            return "很抱歉，這個問題超出我的能力範圍，建議您諮詢專業醫療人員喔。"

    async def _generate_health_response(
        self, user_id: UUID | str, user_input: str, context: str
    ) -> str:
        """
        使用 Health Agent 生成健康照護回覆

        Args:
            user_id: 用戶 ID
            user_input: 用戶輸入
            context: 對話上下文

        Returns:
            健康照護回覆
        """
        try:
            care = self.get_health_agent(user_id)

            task = Task(
                description=(
                    f"{context}"
                    f"使用者輸入：{user_input}\n\n"
                    "你是 COPD 照護助手，請提供溫暖且實用的建議。\n\n"
                    "【知識檢索（RAG）】\n"
                    "- 當需要客觀健康知識時（疾病概念、症狀、風險、就醫時機、"
                    "生活衛教等），請先使用 search_copd_knowledge 工具查找資訊。\n"
                    "- 看到檢索結果後，理解重點並用自己的話回覆，保持對話自然性。\n"
                    "- 如果檢索結果與問題不完全相符，可以適當調整或說明。\n\n"
                    "【回覆原則】\n"
                    "- 語氣溫暖親切，讓用戶感受到關心\n"
                    "- 提供實用建議，避免過於專業的醫學術語\n"
                    "- 必要時提醒用戶就醫或諮詢醫療人員\n"
                    "- 回覆長度：50-150 字\n\n"
                    "【緊急情況處理】\n"
                    "- 如果用戶表達嚴重呼吸困難、胸痛、意識不清等緊急症狀，"
                    "立即建議撥打 119 或前往急診\n"
                    "- 如果用戶表達自殺意圖或嚴重情緒困擾，建議撥打 1925 安心專線"
                ),
                expected_output="溫暖且實用的健康照護建議（50-150字）",
                agent=care,
            )

            response = (
                Crew(agents=[care], tasks=[task], verbose=False).kickoff().raw or ""
            ).strip()

            return (
                response
                or "很抱歉，我現在無法提供建議。建議您諮詢專業醫療人員，或稍後再試。"
            )

        except Exception as e:
            print(f"[Health Response Error] {e}")

            # Fallback: 使用 OpenAI + RAG 工具
            return await self._fallback_response(user_input)

    async def _fallback_response(self, user_input: str) -> str:
        """
        Fallback 機制：CrewAI 失敗時使用 OpenAI + RAG

        Args:
            user_input: 用戶輸入

        Returns:
            回覆內容
        """
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # 使用 RAG 工具檢索知識
            rag_result = COPDKnowledgeTool()._run(user_input, top_k=2)

            system_prompt = (
                "你是 COPD 照護助手，用溫暖親切的口吻提供健康建議。"
                "避免過於專業的術語，必要時提醒用戶就醫。"
            )

            user_prompt = (
                f"參考資料：\n{rag_result}\n\n"
                f"用戶問題：{user_input}\n\n"
                "請根據參考資料回答用戶問題，保持回覆簡潔實用（50-150字）。"
            )

            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
                temperature=0.7,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            return (response.choices[0].message.content or "").strip()

        except Exception as e:
            print(f"[Fallback Error] {e}")
            return "很抱歉，系統暫時無法處理您的問題，請稍後再試或諮詢專業醫療人員。"
