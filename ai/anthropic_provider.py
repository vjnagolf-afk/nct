import anthropic
from ai.provider import BaseAIProvider
from core.validators import SystemValidator

class AnthropicProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20240620"):
        """Khởi tạo kết nối với Anthropic API"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name

    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            # Claude tuân thủ System Prompt rất tốt
            response = self.client.messages.create(
                model=self.model_name,
                system=system_prompt,
                max_tokens=4096,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            raw_text = response.content[0].text
            
            # Sử dụng Validator tự viết để làm sạch chuỗi
            clean_json = SystemValidator.clean_and_validate_json(raw_text)
            return clean_json
            
        except Exception as e:
            raise Exception(f"Lỗi hệ thống khi gọi Anthropic API: {str(e)}")
