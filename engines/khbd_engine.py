# engines/khbd_engine.py
import json
from core.models_khbd import KhbdSchema
from core.validators import SystemValidator

class KhbdEngine:
    @staticmethod
    def generate_export_data(raw_ai_output: str) -> dict:
        """
        Nhận chuỗi thô từ AI, làm sạch qua Validator, 
        ép kiểu vào Pydantic Schema và trả về Dictionary phẳng cho WordExporter.
        """
        clean_json_str = SystemValidator.clean_and_validate_json(raw_ai_output)
        
        try:
            data_dict = json.loads(clean_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Không thể phân tích JSON từ AI: {str(e)}")

        # Xác thực qua Pydantic Schema
        validated_schema = KhbdSchema(**data_dict)
        
        # Trả về dictionary để truyền vào KhbdWordExporter
        return validated_schema.model_dump()
