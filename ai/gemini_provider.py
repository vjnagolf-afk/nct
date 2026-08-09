# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py
Nhiệm vụ: Cung cấp giao tiếp chuẩn với Gemini API, có bộ lọc 
nhận diện loại khóa (API Key vs Google Cloud OAuth Token).
============================================================
"""

import google.generativeai as genai
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        
        # Kiểm tra xem kỹ sư có vô tình dán nhầm Token Google Cloud / OAuth (AQ...) vào ô API Key không
        if self.api_key.startswith("AQ.") or "ya29." in self.api_key:
            raise ValueError(
                "🔑 PHÁT HIỆN DÙNG NHẦM TOKEN GOOGLE CLOUD (DẠNG AQ...):\n"
                "Bạn đang sử dụng Token/Credential của Google Cloud hoặc OAuth, nhưng hệ thống "
                "đang gọi đến endpoint Google AI Studio (generativelanguage.googleapis.com).\n"
                "Endpoint này CHỈ CHẤP NHẬN API Key chuẩn từ Google AI Studio (bắt đầu bằng 'AIza...').\n"
                "👉 Vui lòng tạo API Key mới tại: https://aistudio.google.com/app/apikey và cập nhật lại vào Secrets/Cấu hình AI!"
            )
        
        genai.configure(api_key=self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            generation_config = {
                "temperature": 0.2,
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
