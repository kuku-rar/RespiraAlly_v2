"""
COPD Guardrail Tool - Safety Check for User Input

使用 OpenAI 判斷用戶輸入是否安全（COPD 醫療場景）
"""

import os
from typing import Type

from crewai.tools import BaseTool
from openai import OpenAI
from pydantic import BaseModel, Field


class GuardrailInput(BaseModel):
    """GuardrailTool 輸入參數"""

    user_input: str = Field(..., description="用戶輸入的文本")


class GuardrailTool(BaseTool):
    """
    COPD 安全檢查工具

    判斷用戶輸入是否需要攔截（違法/成人內容/不當醫療指導等）
    """

    name: str = "copd_guardrail_check"
    description: str = (
        "檢查用戶輸入是否安全。返回 'OK' 表示安全可處理，"
        "返回 'BLOCK: <原因>' 表示需要攔截。"
    )
    args_schema: Type[BaseModel] = GuardrailInput

    def _run(self, user_input: str) -> str:
        """
        執行安全檢查

        Args:
            user_input: 用戶輸入文本

        Returns:
            "OK" 或 "BLOCK: <原因>"
        """
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            system_prompt = """
你是一個嚴謹的安全審查器，專門用於 COPD（慢性阻塞性肺病）醫療照護場景。

你的任務是判斷用戶輸入是否需要【攔截】。

【允許放行（回覆 OK）】：
1. COPD 症狀/感受描述（呼吸困難、咳嗽、痰液等）
2. 一般衛教/生活建議詢問（運動、飲食、藥物使用等）
3. 情緒表達/求助訊息
4. 自殺念頭/情緒表達（不含具體方法）

【必須攔截（回覆 BLOCK: <原因>）】：
1. 違法/危險行為的教學/交易/規避
2. 成人內容/未成年不當內容
3. 自傷/自殺/自殘的『具體方法指導或鼓勵執行』
4. 醫療診斷/用藥劑量/處置等『具體、個案化、可執行』的專業指示
   （例如："你需要吃 XX 毫克的 XX 藥"）
5. 法律/投資/稅務等『具體、可執行』的專業指導

【判斷原則】：
- 症狀詢問 ≠ 診斷要求 → OK
- 藥物資訊詢問 ≠ 劑量建議 → OK
- 情緒低落 ≠ 自殺計畫 → OK
- 不確定時一律回 OK（讓後續 Health Agent 判斷緊急性）

【輸出格式】：
- 安全：僅輸出 "OK"
- 需攔截：僅輸出 "BLOCK: <簡短原因>"
""".strip()

            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
                temperature=0,  # 確保一致性
                max_tokens=50,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"請判斷此輸入是否需要攔截：\n\n「{user_input}」",
                    },
                ],
            )

            result = (response.choices[0].message.content or "").strip()

            # 確保輸出格式正確
            if result.startswith("BLOCK"):
                return result
            else:
                return "OK"

        except Exception as e:
            # 發生錯誤時預設為安全（fail-open），避免阻擋正常對話
            print(f"[GuardrailTool Error] {e}")
            return "OK"
