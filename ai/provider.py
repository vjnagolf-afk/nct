from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    """Lớp cơ sở quy định cấu trúc cho mọi AI Provider."""
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        """
        Hàm cốt lõi để gọi API. Bắt buộc các class con phải ép API
        trả về định dạng JSON thuần túy (không chứa ký tự thừa).
        """
        pass
