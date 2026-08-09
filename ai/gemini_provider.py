# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py
Nhiệm vụ: Cung cấp giao tiếp chuẩn với Gemini API.
ĐÃ VÁ LỖI: Sửa triệt để lỗi 401 ACCESS_TOKEN_TYPE_UNSUPPORTED cho API Key dạng AQ...
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
                "temperature": 0.1,  # Đảm bảo AI bám sát dữ liệu gốc, trích xuất chuẩn bảng biểu
                "response_mime_type": "application/json"
            }
            
            # GIẢI PHÁP VÁ LỖI 401: Ép cấu hình client_options bằng API Key thủ công cho từng phiên gọi
            # Điều này ngăn chặn việc SDK tự động nhận diện nhầm chuỗi 'AQ...' thành Google Cloud Access Token.
            c_options = client_options_lib.ClientOptions(api_key=self.api_key)
            
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                generation_config=generation_config,
                client_options=c_options  # Truyền trực tiếp tùy chọn tài khoản vào đây
            )
            
            response = model.generate_content(prompt)
            return SystemValidator.clean_and_validate_json(response.text)
            
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        try:
            c_options = client_options_lib.ClientOptions(api_key=self.api_key)
            
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                client_options=c_options
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
