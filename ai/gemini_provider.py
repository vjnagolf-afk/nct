import google.generativeai as genai
from ai.provider import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """Khởi tạo kết nối với Gemini API"""
        genai.configure(api_key=api_key)
        self.model_name = model_name
        
        # Ép mô hình LUÔN LUÔN trả về JSON ở cấp độ cấu hình API
        self.generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2 # Nhiệt độ thấp để đảm bảo tính logic và tuân thủ format
        )
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            # Gộp system prompt vào nội dung chính
            full_prompt = f"{system_prompt}\n\nTHÔNG TIN ĐẦU VÀO:\n{prompt}"
            
            # Gọi API
            response = self.model.generate_content(full_prompt)
            
            # Làm sạch dữ liệu trả về phòng trường hợp API vẫn dính thẻ markdown
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "", 1)
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            return raw_text.strip()
            
        except Exception as e:
            raise Exception(f"Lỗi hệ thống khi gọi Gemini API: {str(e)}")
