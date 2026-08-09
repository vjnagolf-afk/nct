# -*- coding: utf-8 -*-
import streamlit as st
import json
from utils.document_reader import DocumentProcessor
from utils.nls_constants import KHUNG_NLS_GV, KHUNG_NLS_HS
from ai.gemini_provider import GeminiProvider
from ai.openai_provider import OpenAIProvider
from ai.master_prompts import KHBD_SYSTEM_PROMPT
from engines.khbd_engine import KhbdEngine  # ĐÃ SỬA: Thêm Engine xử lý dữ liệu giáo án
from exporters.word_khbd import KhbdWordExporter

def init_session_state():
    if "khbd_nls_list" not in st.session_state:
        st.session_state.khbd_nls_list = []
    if "khbd_hoat_dong_list" not in st.session_state:
        st.session_state.khbd_hoat_dong_list = []

def get_nls_framework(loai_khung): 
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS

def add_nls():
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
    items = st.session_state.get("khbd_nls_list", [])
    if not items: return "Không có yêu cầu đặc thù về Năng lực số."
    return "\n".join([f"- Năng lực {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def json_to_markdown_preview(raw_content: str) -> str:
    """ĐÃ SỬA: Hàm hiển thị dữ liệu preview Markdown sư phạm từ chuỗi phẳng JSON"""
    try:
        data = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        md = []
        md.append(f"# 📘 BẢN PREVIEW GIÁO ÁN CHUẨN 5512")
        md.append(f"**Tên bài dạy:** {data.get('TEN_BAI_HOC', '')} | **Môn học:** {data.get('MON_HOC', '')} | **Thời lượng:** {data.get('THOI_LUONG', '')}\n")
        md.append("### I. MỤC TIÊU BÀI HỌC")
        md.append(f"- **Kiến thức:** {data.get('MUC_TIEU_KIEN_THUC', '')}")
        md.append(f"- **Năng lực chung:** {data.get('NANG_LUC_CHUNG', '')}")
        md.append(f"- **Năng lực đặc thù:** {data.get('NANG_LUC_DAC_THU', '')}")
        md.append(f"- **Phẩm chất:** {data.get('PHAM_CHAT', '')}\n")
        md.append("### II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU")
        md.append(f"- **Giáo viên:** {data.get('GIAO_VIEN', '')}")
        md.append(f"- **Học sinh:** {data.get('HOC_SINH', '')}\n")
        md.append("### III. TIẾN TRÌNH DẠY HỌC")
        md.append(f"#### 1. Hoạt động 1: Mở đầu")
        md.append(f"* **Mục tiêu:** {data.get('MUC_TIEU', '')}")
        md.append(f"* **Nội dung:** {data.get('NOI_DUNG', '')}")
        md.append(f"* **Sản phẩm:** {data.get('SAN_PHAM', '')}")
        md.append(f"#### 2. Hoạt động 2: Hình thành kiến thức")
        md.append(f"##### Đơn vị kiến thức 1: {data.get('TEN_HOAT_DONG', '')}")
        md.append(f"* **Nội dung:** {data.get('HD1_NOI_DUNG', '')}")
        md.append(f"* **Sản phẩm:** {data.get('HD1_SAN_PHAM', '')}")
        if data.get('TEN_HOAT_DONG_2'):
            md.append(f"##### Đơn vị kiến thức 2: {data.get('TEN_HOAT_DONG_2', '')}")
            md.append(f"* **Nội dung:** {data.get('HD2_NOI_DUNG', '')}")
            md.append(f"* **Sản phẩm:** {data.get('HD2_SAN_PHAM', '')}")
        return "\n\n".join(md)
    except Exception:
        return str(raw_content)

def render_khbd_ui(is_ai_enabled: bool = True):
    init_session_state()

    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512 & TT18)")
    st.caption("Ứng dụng sức mạnh AI tạo sinh để soạn giáo án chi tiết, trích xuất sâu SGK, bảng biểu và hình ảnh.")
    st.divider()
    
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=3)
    with col2:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học"], index=0)
    with col3:
        so_tiet = st.number_input("Số tiết", min_value=1, max_value=15, value=2)
        
    ten_bai = st.text_input("Tên bài học", placeholder="Nhập chính xác tên bài (VD: Căn bậc 2...)")

    st.subheader("✨ Cấu hình AI & Chế độ")
    c_md1, c_md2 = st.columns(2)
    with c_md1:
        mode = st.radio("Chế độ soạn:", ["tu_dong", "chinh_sua"], format_func=lambda x: "⚡ Tự động soạn từ SGK" if x == "tu_dong" else "📄 Chỉnh sửa giáo án gốc", horizontal=True)
    with c_md2:
        model_name = st.selectbox("Mô hình AI (Định tuyến thông minh)", [
            "Gemini 1.5 Flash (Tốc độ nhanh)",
            "Gemini 1.5 Pro (Phân tích chuyên sâu)",
            "GPT-4o Mini (Ổn định, tiết kiệm)",
            "GPT-4o (Cao cấp, logic xuất sắc)"
        ])

    st.subheader("📤 Tài liệu đầu vào")
    file_sgk = st.file_uploader("📂 Tải lên SGK / Đề cương / Tài liệu gốc chứa bảng biểu, hình ảnh (.docx, .pdf)", type=["pdf", "docx"], accept_multiple_files=True)
    file_ga = []

    if st.button("⚡ TẠO KẾ HOẠCH BÀI DẠY BẰNG AI", type="primary", use_container_width=True):
        if not ten_bai.strip():
            st.warning("⚠️ Vui lòng nhập Tên bài học.")
            return
            
        with st.spinner(f"⏳ Đang gọi [{model_name}] để phân tích toàn diện tài liệu và trích xuất bảng biểu..."):
            try:
                noi_dung_chinh = "\n".join([DocumentProcessor.process_uploaded_file(f) for f in file_sgk]) if file_sgk else ""
                
                yeu_cau = f"Hãy biên soạn giáo án cho bài học sau đây:\n- Tên bài: {ten_bai}\n- Môn học: {mon_hoc} {khoi_lop}\n- Số lượng thời lượng bài giảng: {so_tiet} tiết.\n"
                yeu_cau += "YÊU CẦU ĐẶC BIỆT: Hãy đọc thật kỹ nội dung văn bản nguồn, bóc tách toàn bộ số liệu bài tập toán học, các bảng thông tin, trích nguyên văn câu hỏi vào các khóa tương ứng trong cấu trúc dữ liệu JSON đầu ra. Tuyệt đối không được làm ngắn gọn."
                
                prompt_hien_tai = f"{yeu_cau}\n\nTÀI LIỆU VĂN BẢN GỐC ĐỂ TRÍCH XUẤT:\n{noi_dung_chinh}"

                is_openai = "GPT" in model_name
                # ĐÃ SỬA: Đồng bộ hóa việc lấy API Key từ cả text_input giao diện lẫn st.secrets của hệ thống
                api_key = st.session_state.get('api_key_value') or st.secrets.get("OPENAI_API_KEY" if is_openai else "GEMINI_API_KEY", "")
                
                if not api_key:
                    st.error(f"❌ Không tìm thấy API Key cho mô hình {model_name}. Vui lòng kiểm tra lại cấu hình!")
                    return
                
                if is_openai:
                    provider = OpenAIProvider(api_key, model_name="gpt-4o" if "4o" in model_name and "Mini" not in model_name else "gpt-4o-mini")
                else:
                    provider = GeminiProvider(api_key, model_name="gemini-1.5-pro" if "Pro" in model_name else "gemini-1.5-flash")
                    
                raw_json_str = provider.generate_json(prompt=prompt_hien_tai, system_prompt=KHBD_SYSTEM_PROMPT)

                # ĐÃ SỬA: Đưa chuỗi raw_json_str qua KhbdEngine xử lý để đảm bảo dữ liệu chuẩn hóa dạng Dictionary
                export_dict = KhbdEngine.generate_export_data(raw_json_str)

                st.session_state['current_khbd_data'] = {
                    "is_khbd": True,
                    "title": ten_bai,
                    "mon": mon_hoc,
                    "lop": khoi_lop,
                    "so_tiet": so_tiet,
                    "ai_generated_content": raw_json_str,
                    **export_dict
                }
                st.success("🎉 Hệ thống đã xây dựng giáo án thành công!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {str(e)}")

    khbd_cache = st.session_state.get('current_khbd_data')
    if khbd_cache and khbd_cache.get('is_khbd'):
        st.markdown("---")
        st.markdown(f"### 📊 Kết quả Kế hoạch bài dạy: {khbd_cache['title'].upper()}")
        
        formatted_preview = json_to_markdown_preview(khbd_cache)
        with st.expander("👀 Xem trước Kế hoạch bài dạy chi tiết (Sư phạm)", expanded=True):
            st.markdown(formatted_preview)

        col_down, col_del = st.columns(2)
        with col_down:
            try:
                # Đổ dữ liệu phẳng sang KhbdWordExporter để ghi đè chuẩn xác vào biểu mẫu giáo án có sẵn
                word_bytes = KhbdWordExporter.export_to_word(khbd_cache)
                st.download_button(
                    label="📥 TẢI FILE WORD CHUẨN 5512",
                    data=word_bytes,
                    file_name=f"KHBD_{khbd_cache['title'].replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Lỗi tạo file Word: {e}")
                
        with col_del:
            if st.button("🗑️ Xóa kết quả làm lại", use_container_width=True):
                del st.session_state['current_khbd_data']
                st.rerun()
