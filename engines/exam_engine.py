import json
from core.models_exam import ExamSchema

class ExamEngine:
    """
    Trái tim Logic của Module Đề Kiểm Tra.
    Xử lý dữ liệu JSON từ AI, tính toán Ma trận và chuẩn bị dữ liệu xuất Word.
    """
    
    @staticmethod
    def parse_and_validate(json_string: str) -> ExamSchema:
        """
        Bước 1: Chuyển đổi JSON thô thành Cấu trúc đối tượng (Pydantic Model).
        Đồng thời kích hoạt các trình bảo vệ (Validator) để bắt lỗi AI.
        """
        try:
            # Chuyển chuỗi JSON thành Dictionary Python
            data_dict = json.loads(json_string)
            
            # Ép kiểu vào Pydantic Schema. 
            # Nếu AI thiếu đáp án trắc nghiệm, Pydantic sẽ ném lỗi ngay tại đây.
            validated_data = ExamSchema(**data_dict)
            
            return validated_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"AI không trả về định dạng JSON hợp lệ. Vui lòng thử lại. Lỗi chi tiết: {str(e)}")
        except Exception as e:
            raise ValueError(f"Dữ liệu AI sinh ra vi phạm quy tắc cấu trúc đề thi: {str(e)}")

    @staticmethod
    def calculate_matrix(exam_data: ExamSchema) -> dict:
        """
        Bước 2: Thuật toán tự động quét qua danh sách câu hỏi để lập Bảng Ma Trận.
        Python kiểm soát việc đếm số lượng, tuyệt đối không cho AI tự đếm.
        """
        matrix_data = {}
        # Tổng kết toàn bài
        total_stats = {
            "nhan_biet": {"trac_nghiem": 0, "tu_luan": 0},
            "thong_hieu": {"trac_nghiem": 0, "tu_luan": 0},
            "van_dung": {"trac_nghiem": 0, "tu_luan": 0},
            "van_dung_cao": {"trac_nghiem": 0, "tu_luan": 0}
        }
        
        for cau_hoi in exam_data.danh_sach_cau_hoi:
            chu_de = cau_hoi.chu_de
            muc_do = cau_hoi.muc_do
            loai = cau_hoi.loai_cau_hoi
            
            # Khởi tạo chủ đề nếu chưa có trong ma trận
            if chu_de not in matrix_data:
                matrix_data[chu_de] = {
                    "nhan_biet": {"trac_nghiem": 0, "tu_luan": 0},
                    "thong_hieu": {"trac_nghiem": 0, "tu_luan": 0},
                    "van_dung": {"trac_nghiem": 0, "tu_luan": 0},
                    "van_dung_cao": {"trac_nghiem": 0, "tu_luan": 0}
                }
            
            # Tăng biến đếm cho chủ đề (Dùng cho Bảng Đặc Tả và Ma Trận)
            matrix_data[chu_de][muc_do][loai] += 1
            
            # Tăng biến đếm tổng (Dùng cho phần trăm điểm)
            total_stats[muc_do][loai] += 1
            
        return {
            "chi_tiet_chu_de": matrix_data,
            "tong_hop": total_stats,
            "tong_so_cau": exam_data.tong_so_cau
        }

    @staticmethod
    def generate_export_data(json_string: str) -> dict:
        """
        Hàm trung tâm đóng gói toàn bộ dữ liệu sạch để chuyển xuống Tầng Giao Diện (UI) 
        hoặc Tầng Xuất File (Exporters).
        """
        # 1. Xác thực và làm sạch dữ liệu
        exam_obj = ExamEngine.parse_and_validate(json_string)
        
        # 2. Tính toán ma trận toán học
        matrix = ExamEngine.calculate_matrix(exam_obj)
        
        # 3. Đóng gói trả về
        return {
            "tieu_de": exam_obj.tieu_de_de_thi,
            "danh_sach_cau_hoi": exam_obj.danh_sach_cau_hoi,
            "ma_tran": matrix
        }
