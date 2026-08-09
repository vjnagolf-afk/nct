# engines/khbd_engine.py
import json
from core.models_khbd import KhbdSchema
from core.validators import SystemValidator

class KhbdEngine:
    @staticmethod
    def generate_export_data(raw_ai_output: str) -> dict:
        """
        Xử lý, làm sạch và ép kiểu dữ liệu KHBD từ AI,
        đảm bảo giữ nguyên các thẻ trích dẫn bảng biểu và hình ảnh.
        """
        clean_json_str = SystemValidator.clean_and_validate_json(raw_ai_output)
        
        try:
            data_dict = json.loads(clean_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Không thể phân tích JSON từ AI: {str(e)}")

        validated_schema = KhbdSchema(**data_dict)
        return validated_schema.model_dump()
