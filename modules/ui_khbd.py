import streamlit as st
import time
import json
from utils.document_reader import DocumentProcessor
from ai.gemini_provider import GeminiProvider
from ai.master_prompts import KHBD_SYSTEM_PROMPT
from engines.khbd_engine import KhbdEngine
from exporters.word_khbd import KhbdWordExporter

def init_session_state():
    if "hoat_dong_list" not in st.session_state:
        st.session_state.hoat_dong_list = []

def add_hoat_dong():
    new_hd = st.session_state.get("new_hoat_dong", "").strip()
    if new_hd and new_hd not in st.session_state.hoat_dong_list:
        st.session_state.hoat_dong_list.append(new_hd)
    st.session_state["new_hoat_dong"] = "" # Xóa trắng input sau khi thêm

def render_khbd_ui(is_ai_enabled: bool = True):
    init_session_state()

    # Nhúng CSS tùy chỉnh để làm nút bấm màu tím và tinh chỉnh khoảng cách
    st.markdown("""
        <style>
        /* Tùy chỉnh màu sắc nút bấm chính (Primary Button) thành màu tím */
        .stButton button[kind="primary"] {
            background-color: #9333ea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #7e22ce;
            border: none;
        }
        
        /* Tùy chỉnh màu sắc nút outline */
        .stButton button[kind="secondary"] {
            color: #4b5563;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton button[kind="secondary"]:hover {
            border-color: #9333ea;
            color: #9333ea;
        }
        
        /* Giảm khoảng cách giữa các phần tử để UI gọn gàng như bản thiết kế */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # =======================================================
    # 1. THÔNG TIN BÀI DẠY
    # =======================================================
    st.markdown("### 🎛️ Thông tin bài dạy")
    c_khoi, c_mon = st.columns(2)
    with c_khoi:
        khoi_lop = st.selectbox("KHỐI LỚP", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=3)
    with c_mon:
        mon_hoc = st.selectbox("MÔN HỌC", ["Khoa học tự nhiên", "Toán", "Ngữ văn", "Tin học", "Công nghệ"], index=0)

    st.write("") 

    # =======================================================
    # 2. CHẾ ĐỘ TÍCH HỢP (CARDS)
    # =======================================================
    st.markdown("#### ✨ Chế độ tích hợp")
    c_th1, c_th2, c_th3 = st.columns(3)
    
    with c_th1:
        with st.container(border=True):
            tich_hop_nls = st.checkbox("**Tích hợp Năng lực số (NLS)**", help="Lồng ghép NLS theo PPCT", value=True)
            st.caption("Lồng ghép NLS theo PPCT")
            
    with c_th2:
        with st.container(border=True):
            tich_hop_ai = st.checkbox("**Tích hợp Năng lực AI**", help="Lồng ghép AI theo Bảng yêu cầu")
            st.caption("Lồng ghép AI theo Bảng yêu cầu")
            
    with c_th3:
        with st.container(border=True):
            tich_hop_kt = st.checkbox("**Tích hợp Dạy học khuyết tật hòa nhập**", help="Lồng ghép hỗ trợ HSKT")
            st.caption("Lồng ghép hỗ trợ HSKT")

    st.write("")
    st.divider()

    # =======================================================
    # 3. THÔNG TIN GIÁO ÁN SOẠN MỚI
    # =======================================================
    st.markdown("### 📄 Thông tin giáo án soạn mới")
    
    c_cap, c_mau = st.columns(2)
    with c_cap:
        cap_hoc = st.selectbox("Cấp học", ["THCS", "Tiểu học", "THPT"], index=0)
    with c_mau:
        mau_giao_an = st.selectbox("Mẫu giáo án", ["Công văn 5512 (Chuẩn Bộ)", "Mẫu rút gọn", "Mẫu tư duy"])

    c_ten, c_tg = st.columns(2)
    with c_ten:
        ten_bai = st.text_input("Tên bài dạy", placeholder="VD: Khúc xạ ánh sáng")
    with c_tg:
        thoi_gian = st.text_input("Thời lượng (Số tiết)", placeholder="VD: 2 tiết")

    # =======================================================
    # 4. TẢI LÊN TÀI LIỆU
    # =======================================================
    st.markdown("**Tài liệu tham khảo / SGK cơ sở**")
    with st.container(border=True):
        sgk_files = st.file_uploader(
            "Kéo thả hoặc Nhấn để tải lên Sách Giáo Khoa", 
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Hỗ trợ định dạng PDF, DOCX (Tối đa 50MB)"
        )

    # =======================================================
    # 5. KẾ HOẠCH HOẠT ĐỘNG
    # =======================================================
    st.markdown("**Kế hoạch Hoạt động (Tùy chọn)**")
    st.caption("Nhập các hoạt động cần thiết, AI sẽ tự động phân rã nếu để trống.")
    
    c_input, c_add = st.columns([4, 1])
    with c_input:
        st.text_input(
            "Nhập hoạt động", 
            placeholder="VD: Tìm hiểu hiện tượng khúc xạ...", 
            key="new_hoat_dong", 
            label_visibility="collapsed",
            on_change=add_hoat_dong 
        )
    with c_add:
        st.button("Thêm", on_click=add_hoat_dong, type="primary", use_container_width=True)
    
    if st.session_state.hoat_dong_list:
        for i, hd in enumerate(st.session_state.hoat_dong_list):
            c_tag1, c_tag2 = st.columns([11, 1])
            with c_tag1:
                st.info(f"📍 {hd}")
            with c_tag2:
                if st.button("❌", key=f"del_{i}", help="Xóa"):
                    st.session_state.hoat_dong_list.remove(hd)
                    st.rerun()

    st.write("")

    # =======================================================
    # 6. KHỐI HIỂN THỊ CÓ ĐIỀU KIỆN
    # =======================================================
    co_yc_nls = False
    yeu_cau_nls_text = ""
    loai_kt = []

    if tich_hop_nls or tich_hop_ai:
        st.markdown("### 📤 Tài liệu tích hợp bổ sung")
        c_tl1, c_tl2 = st.columns(2)
        
        if tich_hop_nls:
            with c_tl1:
                with st.container(border=True):
                    st.file_uploader("📄 Tải lên PPCT (Năng lực số)", type=["pdf", "docx", "xlsx"])
                    
        if tich_hop_ai:
            with c_tl2:
                with st.container(border=True):
                    st.markdown("[Chuyển sang công cụ Tạo Bảng AI ↗](#)", unsafe_allow_html=True) 
                    st.file_uploader("📋 Tải lên Bảng tích hợp AI", type=["pdf", "docx", "xlsx"])

    if tich_hop_kt:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn dạng khuyết tật hòa nhập")
            st.caption("Giáo án sẽ được điều chỉnh cho phù hợp (chọn nhiều nếu cần)")
            
            danh_sach_kt = [
                "Khuyết tật vận động", "Khuyết tật nghe", "Khuyết tật nói", 
                "Khuyết tật nhìn", "Khuyết tật thần kinh", "Khuyết tật tâm thần", 
                "Khuyết tật trí tuệ", "Khuyết tật tự kỷ", "Khuyết tật khác", 
                "Khuyết tật chung"
            ]
            
            # Sử dụng st.pills (yêu cầu Streamlit >= 1.40)
            loai_kt = st.pills(
                "Chọn khuyết tật", 
                danh_sach_kt, 
                selection_mode="multi", 
                label_visibility="collapsed",
                default=["Khuyết tật chung"]
            )

    if tich_hop_nls:
        with st.container(border=True):
            co_yc_nls = st.checkbox("🎯 **Yêu cầu Năng lực số cụ thể (Tùy chọn)**")
            if co_yc_nls:
                yeu_cau_nls_text = st.text_area("Chỉ định rõ thành phần và mức độ NLS cho AI", placeholder="Nhập yêu cầu tại đây...")

    # =======================================================
    # 7. TÙY CHỌN NGÔN NGỮ & NÚT KÍCH HOẠT CHÍNH
    # =======================================================
    st.write("")
    with st.container(border=True):
        giao_an_ta = st.checkbox("Giáo án viết bằng ngôn ngữ Tiếng Anh")

    st.write("")
    
    btn_text = "⚡ KÍCH HOẠT XỬ LÝ AI" if is_ai_enabled else "📝 TẠO KHUNG GIÁO ÁN CHUẨN (KHÔNG AI)"
    btn_kich_hoat = st.button(btn_text, type="primary", use_container_width=True)
    
    if btn_kich_hoat:
        if not ten_bai:
            st.error("⚠️ Vui lòng nhập Tên bài học.")
            return

        if is_ai_enabled:
            if not sgk_files:
                st.error("⚠️ Vui lòng tải lên tài liệu SGK cơ sở để làm nền tảng biên soạn.")
                return
                
            with st.spinner("Hệ thống AI đang bắt đầu xử lý theo cấu hình của thầy/cô..."):
                try:
                    # Đọc gộp tất cả các file được upload
                    noi_dung_sgk = ""
                    for f in sgk_files:
                        noi_dung_sgk += DocumentProcessor.process_uploaded_file(f) + "\n\n"
                    
                    # Cấu trúc hóa các yêu cầu tích hợp cho Prompt
                    yeu_cau_tich_hop = ""
                    if tich_hop_kt and loai_kt: 
                        yeu_cau_tich_hop += f"- Tích hợp phương pháp dạy học cho HS khuyết tật: {', '.join(loai_kt)}\n"
                    if tich_hop_nls: 
                        yeu_cau_tich_hop += "- Tích hợp năng lực số (Thông tư 18) vào bài học.\n"
                        if co_yc_nls and yeu_cau_nls_text:
                            yeu_cau_tich_hop += f"  + Yêu cầu NLS cụ thể: {yeu_cau_nls_text}\n"
                    if giao_an_ta:
                        yeu_cau_tich_hop += "- TOÀN BỘ GIÁO ÁN PHẢI ĐƯỢC VIẾT BẰNG TIẾNG ANH (Kể cả tiêu đề).\n"
                    if st.session_state.hoat_dong_list:
                        yeu_cau_tich_hop += f"- Phân bổ bám sát danh sách các hoạt động sau: {', '.join(st.session_state.hoat_dong_list)}\n"

                    prompt_hien_tai = f"""
                    Soạn Kế hoạch bài dạy (Giáo án) theo {mau_giao_an}.
                    - Môn: {mon_hoc} {khoi_lop} ({cap_hoc})
                    - Bài dạy: {ten_bai} ({thoi_gian})
                    {yeu_cau_tich_hop}
                    
                    DỮ LIỆU NGUỒN TỪ SGK:
                    {noi_dung_sgk}
                    """
                    
                    api_key = st.secrets.get("GEMINI_API_KEY", "") 
                    if not api_key:
                        st.error("❌ Không tìm thấy API Key.")
                        return
                    
                    provider = GeminiProvider(api_key=api_key)
                    raw_json = provider.generate_json(prompt=prompt_hien_tai, system_prompt=KHBD_SYSTEM_PROMPT)
                    thong_tin_dong_goi = KhbdEngine.generate_export_data(raw_json)
                    
                    st.session_state['khbd_data_clean'] = thong_tin_dong_goi
                    st.success("🎉 Đã tạo thành công Kế hoạch bài dạy!")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {str(e)}")
        else:
            with st.spinner("Đang tải dữ liệu mẫu..."):
                time.sleep(1)
                st.info("Hệ thống đang chạy ở chế độ Không AI. Vui lòng cấu hình API để tự động sinh giáo án.")

    # =======================================================
    # 8. XUẤT KẾT QUẢ
    # =======================================================
    if 'khbd_data_clean' in st.session_state:
        st.markdown("### 📊 Kết quả phân tích & Đóng gói")
        
        # Nút xuất file Word
        word_bytes = KhbdWordExporter.export_khbd(st.session_state['khbd_data_clean'])
        st.download_button(
            label="📥 TẢI XUỐNG GIÁO ÁN HOÀN CHỈNH (.DOCX)",
            data=word_bytes,
            file_name=f"KHBD_{mon_hoc}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )

        with st.expander("👀 Xem trước Cấu trúc Dữ liệu JSON (Kỹ thuật)", expanded=False):
            st.json(st.session_state['khbd_data_clean'])
