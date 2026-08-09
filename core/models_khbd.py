from pydantic import BaseModel, Field, field_validator
from typing import List

class MucTieuSchema(BaseModel):
    """Mô hình phân loại Mục tiêu bài học theo chuẩn GDPT 2018"""
    kien_thuc: List[str] = Field(
        description="Danh sách các yêu cầu cần đạt về kiến thức"
    )
    nang_luc: List[str] = Field(
        description="Danh sách các năng lực chung và năng lực đặc thù cần hình thành"
    )
    pham_chat: List[str] = Field(
        description="Danh sách các phẩm chất chủ yếu được bồi dưỡng trong bài"
    )

class HoatDongSchema(BaseModel):
    """Mô hình cấu trúc cho một Hoạt động dạy học (Chuẩn 5512)"""
    ten_hoat_dong: str = Field(
        description="Tên hoạt động (VD: Hoạt động 1: Mở đầu/Khởi động; Hoạt động 2: Hình thành kiến thức...)"
    )
    thoi_gian_du_kien: int = Field(
        description="Thời gian dự kiến để thực hiện hoạt động này (tính bằng phút)"
    )
    muc_tieu: str = Field(
        description="Mục tiêu cụ thể của riêng hoạt động này"
    )
    noi_dung: str = Field(
        description="Nội dung trọng tâm, câu hỏi hoặc nhiệm vụ giáo viên giao cho học sinh"
    )
    san_pham: str = Field(
        description="Sản phẩm học tập mong đợi (câu trả lời, bài làm, mô hình...) mà học sinh phải hoàn thành"
    )
    to_chuc_thuc_hien: str = Field(
        description="Chi tiết 4 bước: 1. Chuyển giao nhiệm vụ, 2. Thực hiện nhiệm vụ, 3. Báo cáo thảo luận, 4. Kết luận nhận định"
    )

class KhbdSchema(BaseModel):
    """Mô hình cấp cao nhất (Root Schema) cho một Kế hoạch bài dạy hoàn chỉnh"""
    tieu_de_bai_hoc: str = Field(
        description="Tên bài dạy (có thể được AI chuẩn hóa lại cho chuẩn xác)"
    )
    muc_tieu_bai_hoc: MucTieuSchema = Field(
        description="Mục tiêu chung của toàn bộ bài học"
    )
    thiet_bi_hoc_lieu: str = Field(
        description="Danh sách thiết bị, phần mềm, tài liệu cần chuẩn bị (Bao gồm cả cấu hình hòa nhập và năng lực số nếu có)"
    )
    tien_trinh_day_hoc: List[HoatDongSchema] = Field(
        description="Chuỗi các hoạt động dạy học. Bắt buộc phải chia thành các hoạt động rõ ràng."
    )
    
    @field_validator('tien_trinh_day_hoc')
    @classmethod
    def validate_so_luong_hoat_dong(cls, value):
        """Trình bảo vệ: Cảnh báo nếu AI sinh quá ít hoặc quá nhiều hoạt động so với chuẩn"""
        if len(value) < 3 or len(value) > 6:
            raise ValueError("Tiến trình dạy học thường phải có từ 3 đến 6 hoạt động. Hãy kiểm tra lại cấu trúc AI sinh ra.")
        return value
