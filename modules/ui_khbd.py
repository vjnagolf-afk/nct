import streamlit as st
import time
import json
from utils.document_reader import DocumentProcessor
from ai.gemini_provider import GeminiProvider
from ai.master_prompts import KHBD_SYSTEM_PROMPT
from engines.khbd_engine import KhbdEngine

def render_khbd_ui(is_ai_enabled: bool = True):
    st.markdown(
        """
        <style>
        div.stButton > button[kind="primary"] {
            background-color: #e63946 !important;
            color: white !important;
            font-size: 18px !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 15px 0px !important;
            border: none !important;
            transition: all 0.3s ease;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #d62828 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512)")
    st.caption("Biên soạn giáo án tự động từ tài liệu đầu vào. Đảm bảo chuẩn form, chuẩn thời lượng.")
    st.markdown("---")

    # 1. THÔNG TIN BÀI DẠY
    with st.container():
        st.markdown("#### 👥 Thông tin bài dạy")
        col1, col2, col3 = st.columns(3)
        with col1:
            khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=3) # Mặc định Lớp 9
        with col2:
            mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Vật lý", "Hóa học", "Sinh học", "KHTN", "Lịch sử", "Địa lý"], index=6) # Mặc định KHTN
        with col3:
            thoi_gian = st.number_input("Số tiết", min_value=1, max_value=20, value=1, step=1)
            
        ten_bai = st.text_input("Tên bài học", placeholder="VD: Khúc xạ ánh sáng...")
        st.write("") 

    # 2. TÀI LIỆU ĐẦU VÀO
    with st.container():
        st.markdown("#### 🗳️ Tài liệu đầu vào (SGK / Đề cương)")
        uploaded_file_khbd = st.file_uploader("📁 Tải lên file (.docx, .pdf)", type=['pdf', 'docx'], key="file_khbd")
        st.write("")

    # 3. TÍCH HỢP CHUYÊN SÂU
    with st.expander("🛠️ Tích hợp chuyên sâu (Hòa nhập, Năng lực số TT18)", expanded=True):
        cb_hoa_nhap = st.checkbox("🤝 Tích hợp Dạy học hòa nhập (HS Khuyết tật)", value=False)
        dac_diem_hoa_nhap = st.multiselect("Đặc điểm:", ["Vận động", "Nghe", "Nói", "Nhìn", "Trí tuệ", "ADHD"]) if cb_hoa_nhap else []
        
        st.markdown("---")
        cb_nang_luc_so = st.checkbox("💻 Tích hợp Năng lực số (Theo Thông tư 18)", value=True)
        if cb_nang_luc_so:
            st.info("Hệ thống sẽ tự động chỉ đạo AI thiết kế các hoạt động sử dụng thiết bị số (máy chiếu, LMS, phần mềm mô phỏng) phù hợp với bài dạy.")

    st.write("") 

    # 4. NÚT HÀNH ĐỘNG CHÍNH
    btn_text = "⚡ TẠO KẾ HOẠCH BÀI DẠY BẰNG AI" if is_ai_enabled else "📝 TẠO KHUNG GIÁO ÁN CHUẨN (KHÔNG AI)"
    
    if st.button(btn_text, type="primary", use_container_width=True):
        if not ten_bai:
            st.error("⚠️ Vui lòng nhập Tên bài học.")
            return

        if is_ai_enabled:
            if not uploaded_file_khbd:
                st.error("⚠️ Vui lòng tải lên tài liệu đầu vào.")
                return
                
            with st.spinner("Đang biên soạn Kế hoạch bài dạy..."):
                try:
                    noi_dung_sgk = DocumentProcessor.process_uploaded_file(uploaded_file_khbd) 
                    
                    yeu_cau_tich_hop = ""
                    if cb_hoa_nhap: yeu_cau_tich_hop += f"- Lưu ý phương pháp cho HS khuyết tật: {', '.join(dac_diem_hoa_nhap)}\n"
                    if cb_nang_luc_so: yeu_cau_tich_hop += "- Yêu cầu bắt buộc: Ứng dụng năng lực số, công nghệ thông tin (theo Thông tư 18) vào bài học.\n"

                    prompt_hien_tai = f"""
                    Soạn Kế hoạch bài dạy (Giáo án) chuẩn 5512.
                    - Môn: {mon_hoc} {khoi_lop}
                    - Bài dạy: {ten_bai} ({thoi_gian} tiết)
                    {yeu_cau_tich_hop}
                    
                    DỮ LIỆU NGUỒN:
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

    if 'khbd_data_clean' in st.session_state:
        st.markdown("### 📊 Kết quả phân tích từ Engine")
        with st.expander("👀 Xem trước Cấu trúc Dữ liệu (Sẵn sàng xuất Word)", expanded=True):
            st.json(st.session_state['khbd_data_clean'])
