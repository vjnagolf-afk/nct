# ============================================================
# KHỐI MÃ SỬA LỖI 3: TỰ ĐỘNG LÀM SẠCH VÀ CHẶN LỖI KHÓA GOOGLE
# (Thay thế hàm __init__ cũ trong file ai/gemini_provider.py)
# ============================================================

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
    import google.generativeai as genai
    genai.configure(api_key=self.api_key)
