# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py - PHẦN 1: KHỞI TẠO CLASS
============================================================
"""
import google.generativeai as genai
from core.validators import SystemValidator
from .provider import BaseAIProvider

def helper_check_api_key(key: str):
    """Hàm độc lập kiểm tra định dạng khóa an toàn"""
    cleaned_key = str(key).strip().replace('"', '').replace("'", "")
    if cleaned_key.startswith("ya29.") or cleaned_key.startswith("AQ.") or not cleaned_key.startswith("AIzaSy"):
        raise ValueError(
            "🔑 SỰ CỐ XÁC THỰC - SAI ĐỊNH DẠNG API KEY:\n\n"
            "Khóa bạn vừa nhập KHÔNG PHẢI là API Key chính thức của Google AI Studio.\n"
            "Hệ thống yêu cầu chuỗi khóa chuẩn bắt đầu bằng các ký tự 'AIzaSy...'"
        )
    return cleaned_key

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = helper_check_api_key(api_key)
        self.model_name = model_name
        genai.configure(api_key=self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        return execute_gemini_json(self.model_name, prompt, system_prompt)

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        return execute_gemini_text(self.model_name, prompt, system_prompt)
# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py - PHẦN 2: HÀM THỰC THI SÁT LỀ TRÁI
============================================================
"""

def execute_gemini_json(model_name: str, prompt: str, system_prompt: str) -> str:
    """Hàm xử lý sinh cấu trúc dữ liệu JSON thô"""
    try:
        generation_config = {
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config=generation_config
        )
        response = model.generate_content(prompt)
        return SystemValidator.clean_and_validate_json(response.text)
    except Exception as e:
        err_msg = str(e)
        if "ACCESS_TOKEN_TYPE_UNSUPPORTED" in err_msg or "401 Request had invalid authentication" in err_msg:
            raise Exception("🔑 LỖI 401: Vui lòng dùng API Key từ Google AI Studio (AIzaSy...).")
        raise Exception(f"Lỗi khi gọi Gemini API: {err_msg}")

def execute_gemini_text(model_name: str, prompt: str, system_prompt: str) -> str:
    """Hàm xử lý sinh văn bản tự do ngoài cấu trúc"""
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
