# engines/khbd_engine.py
import json
from core.models_khbd import KhbdSchema
from core.validators import SystemValidator

class KhbdEngine:
    @staticmethod
    def generate_export_data(raw_ai_output: str) -> dict:
        """
        Làm sạch chuỗi dữ liệu phản hồi từ AI, kiểm tra lỗi cú pháp JSON dấu phẩy thừa
        và chuyển đổi ép kiểu chặt chẽ vào KhbdSchema.
        """
        # Sử dụng SystemValidator hiện tại để gỡ bỏ dấu bọc markdown ```json ... ```
        clean_json_str = SystemValidator.clean_and_validate_json(raw_ai_output)
        
        try:
            data_dict = json.loads(clean_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi hệ thống: Chuỗi phản hồi từ AI không thể phân rã thành JSON dict: {str(e)}")

        # Ép kiểu vào Pydantic để tự động sửa hoặc bù đắp các trường dữ liệu thiếu hụt bằng chuỗi rỗng
        validated_schema = KhbdSchema(**data_dict)
        return validated_schema.model_dump()
