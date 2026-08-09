# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py
Nhiệm vụ: Giao tiếp với Gemini API, tương thích hoàn toàn API Key AQ...
============================================================
"""

import google.generativeai as genai
from google.api_core import client_options as client_options_lib
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("🔑 Lỗi: API Key cho Gemini không được để trống!")

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            generation_config = {
                "temperature": 0.1,  # Đặt mức thấp nhất để AI tập trung trích xuất chính xác tài liệu gốc
                "response_mime_type": "application/json"
            }
            
            # ĐÃ SỬA: Cấu hình client_options thông qua genai.configure() thay vì truyền vào GenerativeModel
            c_options = client_options_lib.ClientOptions(api_key=self.api_key)
            genai.configure(client_options=c_options)
            
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
            c_options = client_options_lib.ClientOptions(api_key=self.api_key)
            genai.configure(client_options=c_options)
            
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
