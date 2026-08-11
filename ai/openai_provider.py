# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/openai_provider.py
Nhiệm vụ: Cung cấp giao tiếp chuẩn với OpenAI API.
============================================================
"""

import openai
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            if "json" not in system_prompt.lower() and "json" not in prompt.lower():
                system_prompt = (system_prompt + "\n\nImportant: You must return the final output strictly as a valid JSON object.").strip()

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            raw_text = response.choices[0].message.content
            return SystemValidator.clean_and_validate_json(raw_text)
            
        except Exception as e:
            raise Exception(f"Lỗi khi gọi OpenAI API: {str(e)}")

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Lỗi khi gọi OpenAI API: {str(e)}")
