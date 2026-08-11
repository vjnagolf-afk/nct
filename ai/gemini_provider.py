# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py
Nhiệm vụ: Cung cấp giao tiếp chuẩn với Gemini API, chặn đứng
và cảnh báo khi người dùng dán nhầm Token OAuth 2.0.
============================================================
"""

import google.generativeai as genai
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        
        # Nhận diện cơ bản các chuỗi Token GCP OAuth
        if self.api_key.startswith("ya29.") or self.api_key.startswith("AQ."):
            raise ValueError(
                "🔑 PHÁT HIỆN LỖI API KEY:\n"
                "Khóa bạn đang nhập là Token OAuth 2.0 của Google Cloud Platform.\n"
                "Hệ thống hiện tại (generativelanguage.googleapis.com) yêu cầu bắt buộc phải là API Key của Google AI Studio.\n"
                "👉 Hãy truy cập: https://aistudio.google.com/app/apikey để tạo khóa mới (bắt đầu bằng 'AIza...')."
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
            err_msg = str(e)
            # Bắt chính xác thông điệp lỗi 401 của Google gửi về
            if "ACCESS_TOKEN_TYPE_UNSUPPORTED" in err_msg or "401 Request had invalid authentication" in err_msg:
                raise Exception(
                    "🔑 LỖI 401 (TỪ CHỐI XÁC THỰC TỪ GOOGLE):\n"
                    "Google đã từ chối khóa API của bạn do nó được định dạng như một OAuth 2.0 Token.\n"
                    "👉 Hệ thống cần API Key tiêu chuẩn từ Google AI Studio (bắt đầu bằng chữ 'AIza...').\n"
                    "Vui lòng tạo khóa mới tại https://aistudio.google.com/app/apikey và cập nhật lại vào ô cấu hình."
                )
            raise Exception(f"Lỗi khi gọi Gemini API: {err_msg}")

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
