# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py
Nhiệm vụ: Cung cấp giao tiếp chuẩn với Gemini API, chặn đứng
và cảnh báo khi người dùng dán nhầm Token, tự động làm sạch khóa.
============================================================
"""

import google.generativeai as genai
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        # Tự động loại bỏ mọi dấu cách thừa, dấu nháy kép hoặc ký tự xuống dòng do copy-paste lỗi
        self.api_key = str(api_key).strip().replace('"', '').replace("'", "")
        self.model_name = model_name
        
        # Bộ kiểm định chặn đứng việc nhập nhầm Token GCP OAuth
        if self.api_key.startswith("ya29.") or self.api_key.startswith("AQ.") or not self.api_key.startswith("AIzaSy"):
            raise ValueError(
                "🔑 SỰ CỐ XÁC THỰC - SAI ĐỊNH DẠNG API KEY:\n\n"
                "Khóa bạn vừa nhập KHÔNG PHẢI là API Key chính thức của Google AI Studio.\n"
                "Hệ thống yêu cầu chuỗi khóa chuẩn bắt đầu bằng các ký tự 'AIzaSy...'\n\n"
                "👉 Cách khắc phục:\n"
                "1. Truy cập trang cấp khóa miễn phí: https://aistudio.google.com/app/apikey\n"
                "2. Nhấn nút 'Create API Key' và chọn dự án của bạn.\n"
                "3. Sao chép chuỗi mã mới (AIzaSy...) và dán lại vào ô Cấu hình AI."
            )
        
        # Kích hoạt cấu hình chuẩn của Google AI Studio nếu khóa hợp lệ
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
