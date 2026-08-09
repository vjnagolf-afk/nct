import json
from core.models_khbd import KhbdSchema

class KhbdEngine:
    """
    Trái tim Logic của Module Kế Hoạch Bài Dạy.
    Xử lý dữ liệu JSON từ AI, xác thực cấu trúc 5512 và tính toán thời lượng.
    """
    
    @staticmethod
    def parse_and_validate(json_string: str) -> KhbdSchema:
        """
        Bước 1: Chuyển đổi JSON thô thành Đối tượng Python.
        Nếu AI sinh thiếu mục tiêu, hoặc thiết kế sai số lượng hoạt động, Pydantic sẽ chặn lại.
        """
        try:
            data_dict = json.loads(json_string)
            validated_data = KhbdSchema(**data_dict)
            return validated_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"AI không trả về định dạng JSON hợp lệ cho Giáo án. Lỗi chi tiết: {str(e)}")
        except Exception as e:
            raise ValueError(f"Dữ liệu AI sinh ra vi phạm cấu trúc Kế hoạch bài dạy 5512: {str(e)}")

    @staticmethod
    def process_logic(khbd_data: KhbdSchema) -> dict:
        """
        Bước 2: Python thực hiện các tính toán logic.
        Ví dụ: Cộng tổng thời gian dự kiến của các hoạt động để giáo viên dễ kiểm soát.
        """
        tong_thoi_gian = sum([hoat_dong.thoi_gian_du_kien for hoat_dong in khbd_data.tien_trinh_day_hoc])
        
        return {
            "tieu_de": khbd_data.tieu_de_bai_hoc,
            "muc_tieu": khbd_data.muc_tieu_bai_hoc.model_dump(),
            "thiet_bi": khbd_data.thiet_bi_hoc_lieu,
            "tien_trinh": [hd.model_dump() for hd in khbd_data.tien_trinh_day_hoc],
            "tong_thoi_gian_phut": tong_thoi_gian
        }

    @staticmethod
    def generate_export_data(json_string: str) -> dict:
        """
        Hàm trung tâm đóng gói dữ liệu sạch để chuyển xuống Giao diện hoặc Word Exporter.
        """
        # 1. Xác thực và làm sạch dữ liệu
        khbd_obj = KhbdEngine.parse_and_validate(json_string)
        
        # 2. Xử lý logic và đóng gói
        processed_data = KhbdEngine.process_logic(khbd_obj)
        
        return processed_data
