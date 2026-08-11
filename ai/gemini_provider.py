# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py - PHẦN 1: KHỞI TẠO VÀ XÁC THỰC AN TOÀN
Nhiệm vụ: Cung cấp giao tiếp chuẩn với Gemini API, chặn đứng
và cảnh báo khi người dùng dán nhầm Token OAuth 2.0.
============================================================
"""
import google.generativeai as genai
from core.validators import SystemValidator

# SỬA LỖI IMPORTERROR: Thay thế câu lệnh từ 'from ai.provider import...' 
# sang import tương đối trực tiếp từ file provider.py nằm cùng thư mục 'ai/'.
from .provider import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        # Tự động loại bỏ mọi dấu cách thừa, dấu nháy kép hoặc ký tự xuống dòng do copy-paste lỗi
        self.api_key = str(api_key).strip().replace('"', '').replace("'", "")
        self.model_name = model_name
        
        # Bộ kiểm định chặn đứng việc nhập nhầm Token GCP OAuth (Lỗi ya29 đã gặp trước đó)
        if self.api_key.startswith("ya29.") or self.api_key.startswith("AQ.") or not self.api_key.startswith("AIzaSy"):
            raise ValueError(
                "🔑 SỰ CỐ XÁC THỰC - SAI ĐỊNH DẠNG API KEY:\n\n"
                "Khóa bạn vừa nhập KHÔNG PHẢI là API Key chính thức của Google AI Studio.\n"
                "Hệ thống yêu cầu chuỗi khóa chuẩn bắt đầu bằng các ký tự 'AIzaSy...'\n\n"
                "👉 Cách khắc phục:\n"
                "1. Truy cập trang cấp khóa miễn phí: https://google.com\n"
                "2. Nhấn nút 'Create API Key' và chọn dự án của bạn.\n"
                "3. Sao chép chuỗi mã mới (AIzaSy...) và dán lại vào ô Cấu hình AI."
            )
        
        # Kích hoạt cấu hình chuẩn của Google AI Studio nếu khóa hợp lệ
        genai.configure(api_key=self.api_key)
# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/gemini_provider.py - PHẦN 2: ENGINE XỬ LÝ API
============================================================
"""
# Tiếp nối cấu trúc lớp đối tượng GeminiProvider từ Phần 1

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        """Hàm cốt lõi để gọi API và ép trả về định dạng chuỗi JSON sạch"""
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
            # Bắt chính xác thông điệp lỗi xác thực 401 do Google gửi về để đưa ra cảnh báo tường minh
            if "ACCESS_TOKEN_TYPE_UNSUPPORTED" in err_msg or "401 Request had invalid authentication" in err_msg:
                raise Exception(
                    "🔑 LỖI 401 (TỪ CHỐI XÁC THỰC TỪ GOOGLE):\n"
                    "Google đã từ chối khóa API của bạn do cấu hình định dạng hoặc quyền hạn không đúng.\n"
                    "👉 Hệ thống cần API Key tiêu chuẩn từ Google AI Studio (bắt đầu bằng chữ 'AIza...').\n"
                    "Vui lòng tạo khóa mới tại https://google.com và cập nhật lại vào ô cấu hình."
                )
            raise Exception(f"Lỗi khi gọi Gemini API: {err_msg}")

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """Hàm sinh văn bản tự do không bắt buộc định dạng cấu trúc JSON"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
