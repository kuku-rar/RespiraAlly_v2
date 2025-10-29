"""
Health Agent - COPD Care Companion with RAG

負責提供 COPD 健康照護建議（memory=False 模式 + RAG）
"""

import os
from uuid import UUID

from crewai import Agent, LLM

from respira_ally.tools import COPDKnowledgeTool


def create_health_agent(user_id: UUID | str) -> Agent:
    """
    創建 Health Agent（COPD 照護助手）

    職責：
    - 使用 RAG 提供 COPD 健康知識
    - 溫暖陪伴用戶
    - 必要時提醒就醫

    Args:
        user_id: 用戶 ID（用於個性化）

    Returns:
        CrewAI Agent 實例（memory=False + RAG）
    """
    # 使用適當溫度保持對話自然性
    health_llm = LLM(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        temperature=0.7,  # 較高溫度讓對話更自然
    )

    return Agent(
        role="COPD Care Companion",
        goal=(
            "提供溫暖的 COPD 健康照護建議。"
            "使用知識庫工具查找準確資訊，避免憑空猜測。"
            "必要時提醒用戶就醫。"
        ),
        backstory=(
            f"你是用戶 {user_id} 的 COPD 照護助手。"
            "你關心用戶的健康，用溫暖親切的口吻提供建議。"
            "你會使用 COPD 知識庫工具查找準確資訊，不會憑空猜測。"
            "當遇到緊急情況或超出能力範圍時，你會建議用戶立即就醫。"
            "你理解 COPD 患者的辛苦，會給予情緒支持。"
        ),
        tools=[
            COPDKnowledgeTool(),  # RAG 知識檢索工具
            # TODO: 未來可加入 AlertCaseManagerTool (緊急通報)
        ],
        verbose=False,  # 不顯示詳細日誌
        allow_delegation=False,  # 不允許委託其他 agent
        llm=health_llm,
        memory=False,  # 不使用內建記憶（遵循 beloved_grandson 模式）
        max_iterations=3,  # 限制最多 3 次迭代（避免過度調用工具）
    )
