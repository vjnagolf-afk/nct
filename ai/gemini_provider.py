# ai/gemini_provider.py
import google.generativeai as genai
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        genai.configure(api_key=self.api_key)

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            # Kết hợp System Prompt vào cấu hình mô hình để ép trả về JSON
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
            raw_text = response.text
            
            return SystemValidator.clean_and_validate_json(raw_text)
            
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
