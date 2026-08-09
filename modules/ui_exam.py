import streamlit as st
import time
import json
from utils.document_reader import DocumentProcessor
from ai.gemini_provider import GeminiProvider
from ai.master_prompts import EXAM_SYSTEM_PROMPT
from engines.exam_engine import ExamEngine

def render_exam_ui(is_ai_enabled: bool = True):
    # ---------------------------------------------------------
    # CSS TÙY CHỈNH CHO NÚT BẤM
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 1. TIÊU ĐỀ CHÍNH
    # ---------------------------------------------------------
    st.markdown("## 📄 TẠO MA TRẬN & ĐỀ KIỂM TRA")
    st.caption("Sinh ma trận chuẩn, bảng đặc tả và đề thi tự động từ tài liệu gốc. Kiểm soát JSON 100%.")
    st.markdown("---")

    # ---------------------------------------------------------
    # 2. KHỐI THÔNG TIN BÀI KIỂM TRA
    # ---------------------------------------------------------
    with st.container():
        st.markdown("#### 📌 Thông tin bài kiểm tra")
        col1, col2, col3 = st.columns(3)
        with col1:
            khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=3)
        with col2:
            mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Vật lý", "Hóa học", "Sinh học", "KHTN"], index=6)
        with col3:
            loai_bai = st.selectbox("Loại bài", ["Kiểm tra 15 phút", "Kiểm tra 1 tiết (45p)", "Giữa học kì", "Cuối học kì"])
            
        chu_de = st.text_input("Chủ đề / Phạm vi kiến thức", placeholder="VD: Chương 1 - Động lực học chất điểm...")
        st.write("")

    # ---------------------------------------------------------
    # 3. KHỐI CẤU HÌNH MA TRẬN
    # ---------------------------------------------------------
    with st.container():
        st.markdown("#### ⚙️ Thiết lập Ma trận đề")
        col_type1, col_type2 = st.columns(2)
        with col_type1:
            so_cau_tn = st.number_input("Số câu Trắc nghiệm (TN)", min_value=0, max_value=100, value=28, step=1)
        with col_type2:
            so_cau_tl = st.number_input("Số câu Tự luận (TL)", min_value=0, max_value=10, value=3, step=1)

        ti_le = st.select_slider(
            "Tỉ lệ Mức độ nhận thức (Nhận biết : Thông hiểu : Vận dụng : Vận dụng cao)",
            options=["40:30:20:10 (Chuẩn)", "50:30:10:10 (Dễ)", "30:40:20:10 (Khó)"],
            value="40:30:20:10 (Chuẩn)"
        )
        st.write("")

    # ---------------------------------------------------------
    # 4. KHỐI TÀI LIỆU ĐẦU VÀO
    # ---------------------------------------------------------
    with st.container():
        st.markdown("#### 🗳️ Nguồn dữ liệu sinh đề")
        uploaded_file_exam = st.file_uploader("📁 Tải lên Tài liệu tham khảo (.docx, .pdf)", type=['pdf', 'docx'])
        st.write("")

    # ---------------------------------------------------------
    # 5. NÚT HÀNH ĐỘNG & LOGIC KẾT NỐI (AI vs NON-AI)
    # ---------------------------------------------------------
    btn_text = "⚡ TIẾN HÀNH SINH ĐỀ KIỂM TRA (AI)" if is_ai_enabled else "📝 TẠO KHUNG ĐỀ & MA TRẬN MẪU (KHÔNG AI)"
    
    if st.button(btn_text, type="primary", use_container_width=True):
        if not chu_de:
            st.error("⚠️ Vui lòng nhập Chủ đề / Phạm vi kiến thức.")
            return
            
        # ==========================================
        # NHÁNH AI (XỬ LÝ DỮ LIỆU THỰC TẾ)
        # ==========================================
        if is_ai_enabled:
            if not uploaded_file_exam:
                st.error("⚠️ Vui lòng tải lên tài liệu tham khảo để AI trích xuất câu hỏi.")
                return
                
            with st.spinner("Đang đọc tài liệu và phân tích ma trận..."):
                try:
                    # 1. Đọc file
                    noi_dung_goc = DocumentProcessor.process_uploaded_file(uploaded_file_exam)
                    
                    # 2. Chuẩn bị Prompt
                    prompt_hien_tai = f"""
                    Tạo đề kiểm tra môn {mon_hoc} {khoi_lop}. Chủ đề: {chu_de}.
                    Số lượng: {so_cau_tn} câu trắc nghiệm, {so_cau_tl} câu tự luận.
                    Tỉ lệ độ khó mong muốn: {ti_le}.
                    Nội dung tài liệu gốc để lấy kiến thức: 
                    {noi_dung_goc}
                    """
                    
                    # 3. Lấy API Key và gọi AI (Tạm thời dùng Gemini, có thể mở rộng OpenRouter sau)
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                    if not api_key:
                        st.error("❌ Không tìm thấy GEMINI_API_KEY trong hệ thống secrets.")
                        return
                        
                    provider = GeminiProvider(api_key=api_key)
                    
                    # 4. Ép AI sinh JSON
                    raw_json = provider.generate_json(prompt=prompt_hien_tai, system_prompt=EXAM_SYSTEM_PROMPT)
                    
                    # 5. Xác thực qua Pydantic và Tính toán ma trận bằng Python Engine
                    thong_tin_dong_goi = ExamEngine.generate_export_data(raw_json)
                    
                    # Lưu vào session để không bị mất khi load lại trang
                    st.session_state['exam_data_clean'] = thong_tin_dong_goi
                    st.success("🎉 Engine đã xử lý thành công dữ liệu Ma trận và Đề thi!")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống trong quá trình xử lý: {str(e)}")

        # ==========================================
        # NHÁNH KHÔNG AI (LOAD TEMPLATE)
        # ==========================================
        else:
            with st.spinner("Đang tải dữ liệu mẫu..."):
                time.sleep(1)
                st.info("💡 Hệ thống đang chạy ở chế độ Không AI. Vui lòng cấu hình API để tự động sinh câu hỏi. Hiện tại sẽ xuất khung ma trận trống.")
                # Sẽ tích hợp load template Word ở Giai đoạn 4.

    # ---------------------------------------------------------
    # 6. HIỂN THỊ KẾT QUẢ PREVIEW (JSON THUẦN)
    # ---------------------------------------------------------
    if 'exam_data_clean' in st.session_state:
        st.markdown("### 📊 Kết quả phân tích từ Engine")
        with st.expander("👀 Xem trước Cấu trúc Dữ liệu (Sẵn sàng xuất Word)", expanded=True):
            st.json(st.session_state['exam_data_clean'])
