# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py
Nhiệm vụ: Cung cấp giao tiếp chuẩn với Gemini API (Hỗ trợ khóa dạng AQ mới).
============================================================
"""

import google.generativeai as genai
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("🔑 Lỗi: API Key cho Gemini không được để trống!")
            
        # ĐÃ SỬA: Loại bỏ bộ lọc chặn đầu AQ... cũ để chấp nhận các API Key mới từ Google AI Studio
        genai.configure(api_key=self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            generation_config = {
                "temperature": 0.1,  # Giảm temperature xuống để AI bám sát dữ liệu gốc, không tự chế
                "response_mime_type": "application/json"
            }
            
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt)
            return SystemValidator.clean_and_validate_json(response.text)
            
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
