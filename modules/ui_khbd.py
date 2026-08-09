import streamlit as st
import time
from utils.document_reader import DocumentProcessor
from utils.nls_constants import KHUNG_NLS_GV, KHUNG_NLS_HS
from ai.gemini_provider import GeminiProvider
from ai.openai_provider import OpenAIProvider
from ai.master_prompts import KHBD_SYSTEM_PROMPT
from engines.khbd_engine import KhbdEngine
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
        data_tp = get_nls_framework(st.session_state.get("khbd_loai_khung_nls")).get(linh_vuc, {}).get(thanh_phan, {})
        noi_dung = data_tp.get(muc_do, "") if isinstance(data_tp, dict) else data_tp
    except:
        noi_dung = ""

    if noi_dung: 
        item = {"linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
        if item not in st.session_state.khbd_nls_list: 
            st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.get("khbd_nls_list", [])
    if not items: return "Không có yêu cầu đặc thù về Năng lực số."
    return "\n".join([f"- Năng lực {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def render_khbd_ui(is_ai_enabled: bool = True):
    init_session_state()

    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512 & TT18)")
    st.caption("Ứng dụng sức mạnh AI tạo sinh (JSON Architecture) để soạn giáo án bài bản, chống lỗi hoàn hảo.")
    st.divider()
    
    # 1. THÔNG TIN BÀI DẠY
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    with col2:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học", "Lịch sử và Địa lí", "Tin học", "Công nghệ"])
    with col3:
        so_tiet = st.number_input("Số tiết", min_value=1, max_value=15, value=1)
        
    ten_bai = st.text_input("Tên bài học", placeholder="Nhập chính xác tên bài (VD: Định luật Ôm, Thơ Đường luật...)")

    # 2. CẤU HÌNH AI & CHẾ ĐỘ
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

    # 3. TÀI LIỆU ĐẦU VÀO
    st.subheader("📤 Tài liệu đầu vào")
    if mode == "chinh_sua":
        st.info("💡 Chế độ Chỉnh sửa: Hệ thống cần KHBD cũ để làm gốc, và SGK (Tùy chọn) để đối chiếu.")
        col_up1, col_up2 = st.columns(2)
        file_ga = col_up1.file_uploader("📂 Tải lên KHBD cũ (.docx, .pdf)", type=["docx", "pdf"], accept_multiple_files=True)
        file_sgk = col_up2.file_uploader("📂 Tải lên SGK (.docx, .pdf)", type=["pdf", "docx"], accept_multiple_files=True)
    else:
        st.info("💡 Chế độ Tự động: Hệ thống BẮT BUỘC cần Sách giáo khoa hoặc Đề cương để lấy kiến thức.")
        file_sgk = st.file_uploader("📂 Tải lên SGK / Đề cương (.docx, .pdf)", type=["pdf", "docx"], accept_multiple_files=True)
        file_ga = []

    # 4. TÍCH HỢP CHUYÊN SÂU
    with st.expander("🔧 Tích hợp chuyên sâu (Hòa nhập, AI, Số hóa)", expanded=False):
        tich_hop_ai = st.checkbox("🤖 Tích hợp hoạt động sử dụng AI trong bài học")
        tich_hop_hoa_nhap = st.checkbox("🤝 Tích hợp Dạy học hòa nhập (HS Khuyết tật)")
        nhu_cau_hoa_nhap = st.multiselect("Đặc điểm khuyết tật:", ["Vận động", "Nghe", "Nói", "Nhìn", "Trí tuệ", "Tự kỷ / ADHD", "Khác"]) if tich_hop_hoa_nhap else []

        tich_hop_nls = st.checkbox("💻 Tích hợp Năng lực số (Theo Thông tư 18)")
        if tich_hop_nls:
            with st.container(border=True):
                loai_khung = st.radio("Đối tượng áp dụng", ["Giáo viên (Thông tư 18)", "Học sinh (Khung DigComp)"], horizontal=True)
                st.session_state["khbd_loai_khung_nls"] = loai_khung
                
                framework = get_nls_framework(loai_khung)
                col_nls1, col_nls2, col_nls3 = st.columns(3)
                with col_nls1:
                    linh_vuc = st.selectbox("Miền năng lực", list(framework.keys()), key="khbd_nls_linh_vuc")
                with col_nls2:
                    thanh_phan = st.selectbox("Thành phần", list(framework.get(linh_vuc, {}).keys()), key="khbd_nls_thanh_phan")
                with col_nls3:
                    data_tp = framework.get(linh_vuc, {}).get(thanh_phan, {})
                    levels = list(data_tp.keys()) if isinstance(data_tp, dict) else ["Chuẩn chung"]
                    muc_do = st.selectbox("Mức độ", levels, key="khbd_nls_muc_do")
                
                if st.button("➕ Thêm Năng lực số này"):
                    add_nls()
                    
                if st.session_state.khbd_nls_list:
                    st.markdown("**Danh sách NLS đã chọn:**")
                    st.markdown(format_nls())
                    if st.button("🗑️ Xóa danh sách NLS"):
                        st.session_state.khbd_nls_list = []
                        st.rerun()

    st.divider()

    # 5. XỬ LÝ AI
    if st.button("⚡ TẠO KẾ HOẠCH BÀI DẠY BẰNG AI", type="primary", use_container_width=True):
        if not ten_bai.strip():
            st.warning("⚠️ Vui lòng nhập Tên bài học.")
            return
            
        with st.spinner(f"⏳ Đang định tuyến tới [{model_name}] để phân tích JSON KHBD..."):
            try:
                # Bóc tách Text từ file
                noi_dung_chinh = "\n".join([DocumentProcessor.process_uploaded_file(f) for f in file_sgk]) if file_sgk else ""
                noi_dung_ga = "\n".join([DocumentProcessor.process_uploaded_file(f) for f in file_ga]) if file_ga else ""
                
                # Cấu trúc Prompt
                yeu_cau = f"- Soạn KHBD {so_tiet} tiết môn {mon_hoc} {khoi_lop} bài: {ten_bai}.\n"
                if mode == "chinh_sua": yeu_cau += "- Nâng cấp dựa trên KHBD cũ, tham khảo thêm SGK mới.\n"
                if tich_hop_ai: yeu_cau += "- Có lồng ghép hoạt động sử dụng AI.\n"
                if tich_hop_hoa_nhap and nhu_cau_hoa_nhap: yeu_cau += f"- Lưu ý phương pháp cho HS khuyết tật: {', '.join(nhu_cau_hoa_nhap)}.\n"
                if tich_hop_nls and st.session_state.khbd_nls_list: yeu_cau += f"- Tích hợp Năng lực số:\n{format_nls()}\n"
                
                prompt_hien_tai = f"{yeu_cau}\n\nSGK/TÀI LIỆU:\n{noi_dung_chinh}\n\nGIÁO ÁN CŨ:\n{noi_dung_ga}"

                # Định tuyến mô hình (Cross-Routing)
                is_openai = "GPT" in model_name
                api_key = st.secrets.get("OPENAI_API_KEY" if is_openai else "GEMINI_API_KEY", "")
                
                if not api_key:
                    st.error(f"❌ Không tìm thấy API Key cho mô hình {model_name}.")
                    return
                
                # Gọi Engine JSON
                provider = OpenAIProvider(api_key, model_name="gpt-4o" if "4o" in model_name else "gpt-4o-mini") if is_openai else GeminiProvider(api_key, model_name="gemini-1.5-pro" if "Pro" in model_name else "gemini-1.5-flash")
                raw_json = provider.generate_json(prompt=prompt_hien_tai, system_prompt=KHBD_SYSTEM_PROMPT)
                thong_tin_dong_goi = KhbdEngine.generate_export_data(raw_json)
                
                st.session_state['khbd_data_clean'] = thong_tin_dong_goi
                st.success(f"🎉 Engine đã xử lý thành công qua luồng {model_name}!")
                
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {str(e)}")

    # 6. HIỂN THỊ KẾT QUẢ & XUẤT WORD
    if 'khbd_data_clean' in st.session_state:
        st.markdown("### 📊 Kết quả Kế hoạch bài dạy (Chuẩn 5512)")
        
        col_down, col_del = st.columns(2)
        with col_down:
            word_bytes = KhbdWordExporter.export_khbd(st.session_state['khbd_data_clean'])
            st.download_button(
                label="📥 TẢI FILE WORD ĐÚNG CHUẨN 5512",
                data=word_bytes,
                file_name=f"KHBD_{ten_bai.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
        with col_del:
            if st.button("🗑️ Xóa kết quả làm lại", use_container_width=True):
                del st.session_state['khbd_data_clean']
                st.rerun()

        with st.expander("👀 Xem trước Cấu trúc JSON Lõi", expanded=False):
            st.json(st.session_state['khbd_data_clean'])
