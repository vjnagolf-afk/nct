from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal

class OptionSchema(BaseModel):
    """Mô hình dữ liệu cho các phương án đáp án (A, B, C, D)"""
    nhan: Literal["A", "B", "C", "D"] = Field(
        description="Nhãn của đáp án (A, B, C hoặc D)"
    )
    noi_dung: str = Field(
        description="Nội dung chi tiết của phương án lựa chọn"
    )

class QuestionSchema(BaseModel):
    """Mô hình dữ liệu cốt lõi cho một Câu hỏi độc lập"""
    thu_tu: int = Field(
        description="Số thứ tự dự kiến của câu hỏi"
    )
    loai_cau_hoi: Literal["trac_nghiem", "tu_luan"] = Field(
        description="Loại câu hỏi: Trắc nghiệm khách quan hoặc Tự luận"
    )
    muc_do: Literal["nhan_biet", "thong_hieu", "van_dung", "van_dung_cao"] = Field(
        description="Mức độ nhận thức của câu hỏi theo thang Bloom"
    )
    chu_de: str = Field(
        description="Tên chủ đề hoặc đơn vị kiến thức chứa câu hỏi này (Ví dụ: 'Mệnh đề', 'Hệ thức lượng')"
    )
    noi_dung_cau_hoi: str = Field(
        description="Nội dung văn bản chi tiết của câu hỏi"
    )
    danh_sach_dap_an: Optional[List[OptionSchema]] = Field(
        default=None, 
        description="Danh sách 4 phương án. Bắt buộc có nếu là câu trắc nghiệm, bỏ trống nếu là tự luận"
    )
    dap_an_dung: str = Field(
        description="Với trắc nghiệm: Ghi chính xác chữ cái A, B, C hoặc D. Với tự luận: Ghi tóm tắt đáp án cuối cùng."
    )
    huong_dan_giai: str = Field(
        description="Barem chấm điểm chi tiết (cho tự luận) hoặc giải thích các bước giải (cho trắc nghiệm)"
    )

    @field_validator('danh_sach_dap_an')
    @classmethod
    def validate_options_for_multiple_choice(cls, value, info):
        """Trình bảo vệ (Validator): Ép buộc câu trắc nghiệm phải có đủ 4 đáp án"""
        loai = info.data.get('loai_cau_hoi')
        if loai == 'trac_nghiem':
            if not value or len(value) != 4:
                raise ValueError("Câu hỏi trắc nghiệm bắt buộc phải có đúng 4 phương án A, B, C, D.")
        return value
        
    @field_validator('dap_an_dung')
    @classmethod
    def validate_correct_answer(cls, value, info):
        """Trình bảo vệ: Đảm bảo đáp án đúng của câu trắc nghiệm nằm trong [A, B, C, D]"""
        loai = info.data.get('loai_cau_hoi')
        if loai == 'trac_nghiem' and value not in ["A", "B", "C", "D"]:
            raise ValueError(f"Đáp án đúng của câu trắc nghiệm phải là A, B, C hoặc D. Lỗi tại: {value}")
        return value

class ExamSchema(BaseModel):
    """Mô hình cấp cao nhất (Root Schema) đóng gói toàn bộ dữ liệu trả về từ AI"""
    tieu_de_de_thi: str = Field(
        description="Tiêu đề gợi ý cho đề kiểm tra dựa trên nội dung tài liệu"
    )
    danh_sach_cau_hoi: List[QuestionSchema] = Field(
        description="Mảng chứa toàn bộ các câu hỏi trắc nghiệm và tự luận đã được sinh ra"
    )
    
    @property
    def tong_so_cau(self) -> int:
        return len(self.danh_sach_cau_hoi)
        
    @property
    def thong_ke_muc_do(self) -> dict:
        """Hàm tiện ích nội bộ giúp Engine dễ dàng lấy số liệu vẽ Ma trận"""
        thong_ke = {"nhan_biet": 0, "thong_hieu": 0, "van_dung": 0, "van_dung_cao": 0}
        for cau in self.danh_sach_cau_hoi:
            thong_ke[cau.muc_do] += 1
        return thong_ke
