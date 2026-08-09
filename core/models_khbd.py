# core/models_khbd.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class KhbdSchema(BaseModel):
    """Mô hình dữ liệu phẳng (Flat) ánh xạ 1-1 với file Word template."""
    model_config = ConfigDict(extra='allow') # Cho phép AI sinh thêm trường nếu cần

    CHU_DE: str = ""
    TEN_BAI_HOC: str = ""
    MON_HOC: str = ""
    THOI_LUONG: str = ""
    MUC_TIEU_KIEN_THUC: str = ""
    NANG_LUC_CHUNG: str = ""
    NANG_LUC_DAC_THU: str = ""
    NANG_LUC_SO_VA_AI: str = ""
    PHAM_CHAT: str = ""
    GIAO_VIEN: str = ""
    HOC_SINH: str = ""
    
    # HĐ 1
    MUC_TIEU: str = ""
    NOI_DUNG: str = ""
    SAN_PHAM: str = ""
    CHUYEN_GIAO_NHIEM_VU_HOC_TAP: str = ""
    THUC_HIEN_NHIEM_VU_HOC_TAP: str = ""
    BAO_CAO_KET_QUA_VA_THAO_LUAN: str = ""
    DANH_GIA_KET_QUA: str = ""
    
    # HĐ 2.1
    TEN_HOAT_DONG: str = ""
    HD1_MUC_TIEU: str = ""
    HD1_NOI_DUNG: str = ""
    HD1_SAN_PHAM: str = ""
    CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1: str = ""
    THUC_HIEN_NHIEM_VU_HOC_TAP_1: str = ""
    BAO_CAO_KET_QUA_VA_THAO_LUAN_1: str = ""
    KET_LUAN_1: str = ""
    
    # HĐ 2.2
    TEN_HOAT_DONG_2: Optional[str] = ""
    HD2_MUC_TIEU: Optional[str] = ""
    HD2_NOI_DUNG: Optional[str] = ""
    HD2_SAN_PHAM: Optional[str] = ""
    HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP: Optional[str] = ""
    HD2_THUC_HIEN_NHIEM_VU_HOC_TAP: Optional[str] = ""
    HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN: Optional[str] = ""
    HD2_KET_LUAN: Optional[str] = ""
    
    # HĐ 3
    LT_MUC_TIEU: str = ""
    LT_NOI_DUNG: str = ""
    LT_SAN_PHAM: str = ""
    CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT: str = ""
    LT_THUC_HIEN_NHIEM_VU_HOC_TAP: str = ""
    LT_BAO_CAO_KET_QUA_VA_THAO_LUAN: str = ""
    LT_KET_LUAN: str = ""
    
    # HĐ 4
    VD_MUC_TIEU: str = ""
    VD_NOI_DUNG: str = ""
    VD_SAN_PHAM: str = ""
    TO_CHUC_THUC_HIEN: str = ""
    VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP: str = ""
    VD_THUC_HIEN_NHIEM_VU_HOC_TAP: str = ""
    VD_BAO_CAO_KET_QUA_VA_THAO_LUAN: str = ""
    VD_KET_LUAN: str = ""
    
    PHIEU_HOC_TAP: str = ""
