from openai import OpenAI
from ai.provider import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        """Khởi tạo kết nối với OpenAI API"""
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                # Ép buộc ChatGPT phải trả về JSON thuần
                response_format={"type": "json_object"},
                temperature=0.2 
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Lỗi hệ thống khi gọi OpenAI API: {str(e)}")
