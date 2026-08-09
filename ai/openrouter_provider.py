from openai import OpenAI
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class OpenRouterProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "google/gemini-2.5-flash"):
        """Khởi tạo kết nối OpenRouter sử dụng OpenAI SDK"""
        self.client = OpenAI(
            base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",
            api_key=api_key,
        )
        self.model_name = model_name

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            # Vì OpenRouter gọi rất nhiều mô hình khác nhau, tính năng response_format 
            # có thể không được hỗ trợ đồng đều. Ta dùng prompt engineering kết hợp Validator.
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            raw_text = response.choices[0].message.content
            clean_json = SystemValidator.clean_and_validate_json(raw_text)
            return clean_json
            
        except Exception as e:
            raise Exception(f"Lỗi hệ thống khi gọi OpenRouter API: {str(e)}")
