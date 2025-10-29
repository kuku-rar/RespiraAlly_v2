"""
Guardrail Agent - COPD Safety Check

負責檢查用戶輸入的安全性（memory=False 模式）
"""

import os

from crewai import Agent, LLM

from respira_ally.tools import GuardrailTool


def create_guardrail_agent() -> Agent:
    """
    創建 Guardrail Agent

    職責：
    - 判斷用戶輸入是否安全
    - 攔截違法/成人內容/不當醫療指導等
    - 不提供醫療建議，僅做安全檢查

    Returns:
        CrewAI Agent 實例（memory=False）
    """
    # 使用低溫度確保一致性
    guardrail_llm = LLM(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        temperature=0,  # 安全檢查需要確定性
    )

    return Agent(
        role="COPD Safety Guardrail",
        goal="判斷用戶輸入是否需要攔截（安全/法律/醫療等高風險）",
        backstory=(
            "你是一位嚴謹的安全審查專家，專門負責 COPD 醫療照護場景的安全檢查。"
            "你的任務是保護用戶和系統免受不當內容的影響。"
            "你不提供醫療建議，僅做安全性判斷。"
        ),
        tools=[GuardrailTool()],
        verbose=False,  # 不顯示詳細日誌
        allow_delegation=False,  # 不允許委託其他 agent
        llm=guardrail_llm,
        memory=False,  # 不使用內建記憶（遵循 beloved_grandson 模式）
    )
