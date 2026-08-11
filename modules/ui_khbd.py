# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ui_khbd.py - PHẦN 1: KHỞI TẠO VÀ BỔ TRỢ
============================================================
"""
import streamlit as st
import json
import re

try:
    from utils.nls_constants import KHUNG_NLS_GV, KHUNG_NLS_HS
except Exception:
    KHUNG_NLS_GV, KHUNG_NLS_HS = {}, {}

try:
    from ai.gemini_provider import GeminiProvider
except Exception:
    GeminiProvider = None

try:
    from ai.openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None

try:
    from ai.master_prompts import KHBD_SYSTEM_PROMPT
except Exception:
    KHBD_SYSTEM_PROMPT = ""

try:
    import pypdf
    from docx import Document as DocxDocument
except ImportError:
    pypdf = None
    DocxDocument = None

try:
    from exporters.word_khbd import KhbdWordExporter
except Exception:
    KhbdWordExporter = None

def format_latex_for_streamlit(text):
    """Khắc phục lỗi hiển thị công thức Toán học chuẩn Markdown trên Streamlit"""
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    return text

def safe_extract_file(uploaded_file) -> str:
    """Hàm trích xuất văn bản thô từ tệp tin PDF/Word tải lên"""
    text_content = ""
    if uploaded_file is None:
        return text_content
    try:
        file_type = uploaded_file.name.split(".")[-1].lower()
        if file_type == "pdf" and pypdf:
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n"
        elif file_type in ["docx", "doc"] and DocxDocument:
            doc = DocxDocument(uploaded_file)
            for para in doc.paragraphs:
                text_content += para.text + "\n"
        else:
            text_content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Lỗi đọc file {uploaded_file.name}: {e}")
    return text_content

def init_session_state():
    """Khởi tạo các biến trạng thái hệ thống"""
    if "khbd_nls_list" not in st.session_state:
        st.session_state.khbd_nls_list = []
    if "current_khbd_data" not in st.session_state:
        st.session_state.current_khbd_data = None

def get_nls_framework(loai_khung): 
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS
# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ui_khbd.py - PHẦN 2: NĂNG LỰC SỐ VÀ PREVIEW
============================================================
"""
# Tiếp tục nối tiếp các hàm xử lý dữ liệu từ Đoạn 1

def add_nls():
    """Thêm một mục năng lực số được chọn vào danh sách lưu trữ"""
    linh_vuc = st.session_state.get("khbd_nls_linh_vuc", "")
    thanh_phan = st.session_state.get("khbd_nls_thanh_phan", "")
    muc_do = st.session_state.get("khbd_nls_muc_do", "")
    try:
        framework = get_nls_framework(st.session_state.get("khbd_loai_khung_nls", "Giáo viên (Thông tư 18)"))
        data_tp = framework.get(linh_vuc, {}).get(thanh_phan, {})
        noi_dung = data_tp.get(muc_do, "") if isinstance(data_tp, dict) else data_tp
    except Exception:
        noi_dung = ""

    if noi_dung: 
        item = {"linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
        if item not in st.session_state.khbd_nls_list: 
            st.session_state.khbd_nls_list.append(item)

def format_nls():
    """Chuyển đổi danh sách năng lực số thành chuỗi văn bản gửi cho AI"""
    items = st.session_state.get("khbd_nls_list", [])
    if not items: return "Không có yêu cầu đặc thù về Năng lực số."
    return "\n".join([f"- Năng lực {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def json_to_markdown_preview(raw_content: str) -> str:
    """Chuyển đổi chuỗi dữ liệu JSON phẳng của giáo án thành định dạng Markdown hiển thị"""
    try:
        data = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        if not isinstance(data, dict): return str(raw_content)

        md = []
        md.append(f"# KẾ HOẠCH BÀI DẠY: {data.get('TEN_BAI_HOC', '').upper()}")
        md.append(f"**Môn:** {data.get('MON_HOC', '')} | **Thời lượng:** {data.get('THOI_LUONG', '')}\n")
        md.append("---")
        
        md.append("## I. MỤC TIÊU")
        md.append(f"- **Kiến thức:** {data.get('MUC_TIEU_KIEN_THUC', '')}")
        md.append(f"- **Năng lực chung:** {data.get('NANG_LUC_CHUNG', '')}")
        md.append(f"- **Năng lực đặc thù:** {data.get('NANG_LUC_DAC_THU', '')}")
        md.append(f"- **Năng lực số và AI:** {data.get('NANG_LUC_SO_VA_AI', '')}")
        md.append(f"- **Phẩm chất:** {data.get('PHAM_CHAT', '')}\n")

        md.append("## II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU")
        md.append(f"- **Giáo viên:** {data.get('GIAO_VIEN', '')}")
        md.append(f"- **Học sinh:** {data.get('HOC_SINH', '')}\n")

        md.append("## III. TIẾN TRÌNH DẠY HỌC")
        
        md.append("### 1. HOẠT ĐỘNG 1: MỞ ĐẦU / KHỞI ĐỘNG")
        md.append(f"- **Mục tiêu:** {data.get('MUC_TIEU', '')}")
        md.append(f"- **Nội dung:** {data.get('NOI_DUNG', '')}")
        md.append(f"- **Sản phẩm:** {data.get('SAN_PHAM', '')}")
        md.append(f"  - _Chuyển giao nhiệm vụ:_ {data.get('CHUYEN_GIAO_NHIEM_VU_HOC_TAP', '')}")
        md.append(f"  - _Thực hiện nhiệm vụ:_ {data.get('THUC_HIEN_NHIEM_VU_HOC_TAP', '')}")
        md.append(f"  - _Báo cáo, thảo luận:_ {data.get('BAO_CAO_KET_QUA_VA_THAO_LUAN', '')}")
        md.append(f"  - _Đánh giá, kết luận:_ {data.get('DANH_GIA_KET_QUA', '')}\n")

        md.append(f"### 2. {data.get('TEN_HOAT_DONG', 'HOẠT ĐỘNG HÌNH THÀNH KIẾN THỨC 1')}")
        md.append(f"- **Mục tiêu:** {data.get('HD1_MUC_TIEU', '')}")
        md.append(f"- **Nội dung:** {data.get('HD1_NOI_DUNG', '')}")
        md.append(f"- **Sản phẩm:** {data.get('HD1_SAN_PHAM', '')}")
        md.append(f"  - _Chuyển giao:_ {data.get('CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1', '')}")
        md.append(f"  - _Thực hiện:_ {data.get('THUC_HIEN_NHIEM_VU_HOC_TAP_1', '')}")
        md.append(f"  - _Báo cáo:_ {data.get('BAO_CAO_KET_QUA_VA_THAO_LUAN_1', '')}")
        md.append(f"  - _Kết luận:_ {data.get('KET_LUAN_1', '')}\n")

        if data.get('TEN_HOAT_DONG_2'):
            md.append(f"### 3. {data.get('TEN_HOAT_DONG_2', '')}")
            md.append(f"- **Mục tiêu:** {data.get('HD2_MUC_TIEU', '')}")
            md.append(f"- **Nội dung:** {data.get('HD2_NOI_DUNG', '')}")
            md.append(f"- **Sản phẩm:** {data.get('HD2_SAN_PHAM', '')}")
            md.append(f"  - _Chuyển giao:_ {data.get('HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP', '')}")
            md.append(f"  - _Thực hiện:_ {data.get('HD2_THUC_HIEN_NHIEM_VU_HOC_TAP', '')}")
            md.append(f"  - _Báo cáo:_ {data.get('HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN', '')}")
            md.append(f"  - _Kết luận:_ {data.get('HD2_KET_LUAN', '')}\n")

        md.append("### 4. HOẠT ĐỘNG LUYỆN TẬP")
        md.append(f"- **Mục tiêu:** {data.get('LT_MUC_TIEU', '')}")
        md.append(f"- **Nội dung:** {data.get('LT_NOI_DUNG', '')}")
        md.append(f"- **Sản phẩm:** {data.get('LT_SAN_PHAM', '')}")
        md.append(f"  - _Chuyển giao:_ {data.get('CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT', '')}")
        md.append(f"  - _Thực hiện:_ {data.get('LT_THUC_HIEN_NHIEM_VU_HOC_TAP', '')}")
        md.append(f"  - _Báo cáo:_ {data.get('LT_BAO_CAO_KET_QUA_VA_THAO_LUAN', '')}")
        md.append(f"  - _Kết luận:_ {data.get('LT_KET_LUAN', '')}\n")

        md.append("### 5. HOẠT ĐỘNG VẬN DỤNG")
        md.append(f"- **Mục tiêu:** {data.get('VD_MUC_TIEU', '')}")
        md.append(f"- **Nội dung:** {data.get('VD_NOI_DUNG', '')}")
        md.append(f"- **Sản phẩm:** {data.get('VD_SAN_PHAM', '')}")
        md.append(f"  - _Chuyển giao:_ {data.get('VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP', '')}")
        md.append(f"  - _Thực hiện:_ {data.get('VD_THUC_HIEN_NHIEM_VU_HOC_TAP', '')}")
        md.append(f"  - _Báo cáo:_ {data.get('VD_BAO_CAO_KET_QUA_VA_THAO_LUAN', '')}")
        md.append(f"  - _Kết luận:_ {data.get('VD_KET_LUAN', '')}\n")

        if data.get('PHIEU_HOC_TAP'):
            md.append(f"## IV. PHIẾU HỌC TẬP\n{data.get('PHIEU_HOC_TAP', '')}")

        return "\n".join(md)
    except Exception as e:
        return f"Lỗi hiển thị xem trước: {str(e)}\n\nNội dung gốc:\n{raw_content}"
# ============================================================
# KHỐI MÃ SỬA LỖI 1 & 2: CẮT DUNG LƯỢNG CHỐNG TRÀN TOKEN VÀ TPM
# (Thay thế đoạn xử lý chuỗi safe_text cũ trong Phần 3 của ui_khbd.py)
# ============================================================

# 1. Trích xuất dữ liệu thô từ file buffer
extracted_sgk_text = "\n".join([safe_extract_file(f) for f in file_sgk]) if file_sgk else ""
extracted_ga_text = "\n".join([safe_extract_file(f) for f in file_ga]) if file_ga else ""

# 2. Hạ mức giới hạn ký tự xuống mức an toàn tuyệt đối cho tài khoản giới hạn TPM thấp
# Quy đổi: ~35,000 ký tự tiếng Việt tương đương khoảng 10,000 - 12,000 tokens, an toàn cho hạn mức 30,000 TPM
sgk_safe_text = extracted_sgk_text[:35000]
if len(extracted_sgk_text) > 35000:
    sgk_safe_text += "\n\n[...HỆ THỐNG ĐÃ CẮT BỚT SGK ĐỂ CHỐNG QUÁ TẢI TÀI KHOẢN OPENAI CỦA BẠN...]"

ga_safe_text = extracted_ga_text[:15000]
if len(extracted_ga_text) > 15000:
    ga_safe_text += "\n\n[...HỆ THỐNG ĐÃ CẮT BỚT GIÁO ÁN CŨ ĐỂ TRÁNH LỖI RATE LIMIT...]"

# 3. Đóng gói các yêu cầu sư phạm kèm theo
yeu_cau = f"- Soạn KHBD chuẩn 5512 CỰC KỲ CHI TIẾT với thời lượng chính xác {so_tiet} tiết cho môn {mon_hoc} {khoi_lop}, bài: {ten_bai}.\n"
yeu_cau += f"- Bắt buộc phân rã chi tiết rạch ròi theo từng tiết học.\n"
yeu_cau += f"- Tuyệt đối KHÔNG LẶP LẠI tiêu đề mào đầu trong nội dung sinh ra.\n"

if tich_hop_ai: yeu_cau += "- Lồng ghép hoạt động sử dụng AI.\n"
if tich_hop_hoa_nhap and nhu_cau_hoa_nhap: yeu_cau += f"- Lưu ý phương pháp cho HS khuyết tật: {', '.join(nhu_cau_hoa_nhap)}.\n"
if tich_hop_nls and st.session_state.khbd_nls_list: yeu_cau += f"- Tích hợp Năng lực số:\n{format_nls()}\n"

# Tạo chuỗi Prompt cuối cùng đã tối ưu hóa độ dài
prompt_hien_tai = f"{yeu_cau}\n\nSGK / TÀI LIỆU NGUỒN KHÁI QUÁT:\n{sgk_safe_text}\n\nGIÁO ÁN MẪU THAM KHẢO:\n{ga_safe_text}"
