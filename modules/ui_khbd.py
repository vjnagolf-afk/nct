# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ui_khbd.py
Nhiệm vụ: Giao diện Xây dựng KHBD chuẩn 5512
(Bản Kỹ sư trưởng: Xử lý an toàn File Buffer, Form Submit và LaTeX Preview)
============================================================
"""

import streamlit as st
import json
import re
from utils.nls_constants import KHUNG_NLS_GV, KHUNG_NLS_HS
from ai.gemini_provider import GeminiProvider
from ai.openai_provider import OpenAIProvider
from ai.master_prompts import KHBD_SYSTEM_PROMPT

# Import thư viện xử lý file chuyên dụng
try:
    import pypdf
    from docx import Document as DocxDocument
except ImportError:
    pypdf = None
    DocxDocument = None

try:
    from exporters.word_khbd import KhbdWordExporter, export_word
except ImportError:
    KhbdWordExporter = None

def format_latex_for_streamlit(text):
    """Chuyển đổi các định dạng toán học để Streamlit render chính xác"""
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    return text

def safe_extract_file(uploaded_file) -> str:
    """Đọc file an toàn một lần và lưu bộ nhớ, tránh lỗi Buffer Empty"""
    text_content = ""
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
    if "khbd_nls_list" not in st.session_state:
        st.session_state.khbd_nls_list = []
    if "extracted_sgk" not in st.session_state:
        st.session_state.extracted_sgk = ""
    if "extracted_ga" not in st.session_state:
        st.session_state.extracted_ga = ""

def json_to_markdown_preview(raw_content: str) -> str:
    """Biên dịch JSON thô thành Markdown sư phạm đẹp mắt"""
    try:
        data = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        if not isinstance(data, dict): return str(raw_content)
        kb = data.get("Kế hoạch bài dạy", data)
        if not isinstance(kb, dict): kb = data

        md = []
        md.append(f"# KẾ HOẠCH BÀI DẠY: {str(kb.get('Bài', ''))}")
        md.append(f"**Môn:** {kb.get('Môn', '')} | **Lớp:** {kb.get('Lớp', '')} | **Thời gian:** {kb.get('Thời gian', '')}\n")
        md.append("---")

        for k, v in kb.items():
            if k.startswith("Tiết"):
                md.append(f"## 📌 {k.upper()} ({v.get('Thời gian', '')})")
                noi_dung = v.get("Nội dung", {})
                if isinstance(noi_dung, dict):
                    for sec_title, sec_val in noi_dung.items():
                        md.append(f"### 🔹 {sec_title}")
                        if isinstance(sec_val, dict):
                            for sub_k, sub_v in sec_val.items():
                                if isinstance(sub_v, dict):
                                    md.append(f"- **{sub_k}:**")
                                    for sk, sv in sub_v.items():
                                        if isinstance(sv, list):
                                            md.append(f"  - _{sk}:_")
                                            for item in sv: md.append(f"    - {item}")
                                        else: md.append(f"  - _{sk}:_ {sv}")
                                elif isinstance(sub_v, list):
                                    md.append(f"- **{sub_k}:**")
                                    for item in sub_v: md.append(f"  - {item}")
                                else: md.append(f"- **{sub_k}:** {sub_v}")
                        else: md.append(f"{sec_val}")
                md.append("\n")
        return "\n".join(md)
    except Exception:
        return str(raw_content)

def render_khbd_ui(is_ai_enabled: bool = True):
    init_session_state()

    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512)")
    st.divider()
    
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1: khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=3)
    with col2: mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học tự nhiên", "Tin học"], index=0)
    with col3: so_tiet = st.number_input("Số tiết", min_value=1, max_value=15, value=2)
    ten_bai = st.text_input("Tên bài học", placeholder="Nhập chính xác tên bài (VD: Căn bậc 2...)")

    st.subheader("✨ Cấu hình AI & Chế độ")
    c_md1, c_md2 = st.columns(2)
    with c_md1: mode = st.radio("Chế độ soạn:", ["tu_dong", "chinh_sua"], horizontal=True)
    with c_md2: model_name = st.selectbox("Mô hình AI:", ["GPT-4o (Cao cấp, logic xuất sắc)", "GPT-4o Mini (Ổn định, tiết kiệm)", "Gemini 1.5 Pro", "Gemini 1.5 Flash"])

    st.subheader("📤 Tài liệu đầu vào")
    if mode == "chinh_sua":
        col_up1, col_up2 = st.columns(2)
        file_ga = col_up1.file_uploader("📂 Tải lên KHBD cũ", type=["docx", "pdf"], accept_multiple_files=True)
        file_sgk = col_up2.file_uploader("📂 Tải lên SGK", type=["pdf", "docx"], accept_multiple_files=True)
    else:
        file_sgk = st.file_uploader("📂 Tải lên SGK / Đề cương", type=["pdf", "docx"], accept_multiple_files=True)
        file_ga = []

    # Xử lý trích xuất lưu an toàn vào Session State ngay khi Upload
    if file_sgk:
        sgk_names = [f.name for f in file_sgk]
        if st.session_state.get("sgk_files_cache") != sgk_names:
            st.session_state.extracted_sgk = "\n".join([safe_extract_file(f) for f in file_sgk])
            st.session_state.sgk_files_cache = sgk_names
    else:
        st.session_state.extracted_sgk = ""

    if file_ga:
        ga_names = [f.name for f in file_ga]
        if st.session_state.get("ga_files_cache") != ga_names:
            st.session_state.extracted_ga = "\n".join([safe_extract_file(f) for f in file_ga])
            st.session_state.ga_files_cache = ga_names
    else:
        st.session_state.extracted_ga = ""

    st.divider()

    # Bọc luồng kích hoạt bằng st.form để khóa giao diện, chống Reload vô tình
    with st.form("ai_generate_form"):
        st.markdown("**Xác nhận cấu hình và Bắt đầu**")
        submit_button = st.form_submit_button("⚡ TẠO KẾ HOẠCH BÀI DẠY BẰNG AI", type="primary", use_container_width=True)

    if submit_button:
        if not ten_bai.strip():
            st.warning("⚠️ Vui lòng nhập Tên bài học.")
        else:
            with st.spinner(f"⏳ Đang định tuyến tới [{model_name}] để phân tích sâu SGK..."):
                try:
                    yeu_cau = f"- Soạn KHBD chuẩn 5512 CỰC KỲ CHI TIẾT với thời lượng chính xác {so_tiet} tiết cho môn {mon_hoc} {khoi_lop}, bài: {ten_bai}.\n"
                    yeu_cau += f"- Bắt buộc phân rã chi tiết rạch ròi theo từng tiết học (Tiết 1, Tiết 2,...).\n"
                    yeu_cau += f"- Trích xuất cụ thể các định nghĩa, ví dụ, bài tập, câu hỏi, dữ liệu bảng biểu có trong tài liệu SGK dưới đây.\n"
                    
                    prompt_hien_tai = f"{yeu_cau}\n\nSGK / TÀI LIỆU NGUỒN:\n{st.session_state.extracted_sgk}\n\nGIÁO ÁN CŨ:\n{st.session_state.extracted_ga}"

                    is_openai = "GPT" in model_name
                    api_key = st.secrets.get("OPENAI_API_KEY" if is_openai else "GEMINI_API_KEY", "")
                    
                    if not api_key:
                        st.error(f"❌ Không tìm thấy API Key cho {model_name}.")
                    else:
                        if is_openai:
                            provider = OpenAIProvider(api_key, model_name="gpt-4o" if "4o" in model_name and "Mini" not in model_name else "gpt-4o-mini")
                        else:
                            provider = GeminiProvider(api_key, model_name="gemini-1.5-pro" if "Pro" in model_name else "gemini-1.5-flash")
                            
                        raw_json_str = provider.generate_json(prompt=prompt_hien_tai, system_prompt=KHBD_SYSTEM_PROMPT)

                        st.session_state['current_khbd_data'] = {
                            "is_khbd": True, "title": ten_bai, "so_tiet": so_tiet, "ai_generated_content": raw_json_str
                        }
                        st.success(f"🎉 Đã soạn thành công KHBD {so_tiet} tiết qua luồng {model_name}!")
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {str(e)}")

    # 6. HIỂN THỊ KẾT QUẢ CỐ ĐỊNH (Nằm ngoài form)
    khbd_cache = st.session_state.get('current_khbd_data')
    if khbd_cache and khbd_cache.get('is_khbd'):
        st.markdown("---")
        st.markdown(f"### 📊 Kết quả Kế hoạch bài dạy: {khbd_cache['title'].upper()} ({khbd_cache['so_tiet']} tiết)")
        
        # Áp dụng hàm Regex biến đổi LaTeX để hiển thị mượt mà trên Streamlit
        formatted_preview = json_to_markdown_preview(khbd_cache.get('ai_generated_content', ''))
        clean_preview = format_latex_for_streamlit(formatted_preview)
        
        with st.expander("👀 Xem trước Kế hoạch bài dạy chi tiết (Sư phạm)", expanded=True):
            st.markdown(clean_preview)

        col_down, col_del = st.columns(2)
        with col_down:
            try:
                word_bytes = export_word(khbd_cache)
                st.download_button(
                    label="📥 TẢI FILE WORD CHUẨN 5512 (ĐẦY ĐỦ 2 TIẾT, BẢNG, TOÁN)",
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
