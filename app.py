import streamlit as st
from modules.ui_khbd import render_khbd_ui
from modules.ui_exam import render_exam_ui

# ---------------------------------------------------------
# CẤU HÌNH TRANG CƠ BẢN
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Khảo Thí & Soạn Giảng",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# QUẢN LÝ TRẠNG THÁI (SESSION STATE) & NHẬN DIỆN VIP
# ---------------------------------------------------------
def initialize_session():
    if 'has_api_key' not in st.session_state:
        st.session_state['has_api_key'] = False
    if 'api_key_value' not in st.session_state:
        st.session_state['api_key_value'] = ""
        
    # Quét Secrets để tự động kích hoạt chế độ VIP (AI)
    try:
        if "GEMINI_API_KEY" in st.secrets or "OPENROUTER_API_KEY" in st.secrets:
            st.session_state['has_api_key'] = True
            st.session_state['is_vip'] = True
        else:
            st.session_state['is_vip'] = False
    except FileNotFoundError:
        st.session_state['is_vip'] = False

initialize_session()

# ---------------------------------------------------------
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 📚 MENU HỆ THỐNG")
    
    # Hiển thị Trạng thái hoạt động
    if st.session_state.get('is_vip') or st.session_state.get('has_api_key'):
        st.success("🟢 Chế độ AI (VIP): Đã kích hoạt")
        is_ai_enabled = True
    else:
        st.warning("🟡 Chế độ Tiêu chuẩn: Không AI")
        is_ai_enabled = False
        
    st.markdown("---")
    
    # Menu Điều hướng
    menu_selection = st.radio(
        "Điều hướng chức năng",
        ["🏠 Trang chủ", "📘 Xây dựng KHBD (Giáo án)", "📄 Tạo Đề & Ma trận", "⚙️ Cấu hình AI"]
    )
    
    st.markdown("---")
    st.caption("Phiên bản Hệ thống: Enterprise 2.0")
    st.caption("Kiến trúc: Python Logic + AI Data Schema")

# ---------------------------------------------------------
# BỘ ĐỊNH TUYẾN (ROUTER) CHÍNH
# ---------------------------------------------------------
if menu_selection == "🏠 Trang chủ":
    st.title("🎓 Hệ thống Trợ lý Sư phạm Thông minh")
    st.markdown("""
    Chào mừng thầy/cô đến với cỗ máy soạn giảng và khảo thí tự động, được thiết kế tối ưu chuyên sâu cho Chương trình GDPT 2018 (đặc biệt phát huy sức mạnh với các môn đòi hỏi độ chính xác cao như Khoa học tự nhiên, Toán học).
    
    **Các tính năng cốt lõi:**
    *   **Tạo Đề Kiểm Tra & Ma Trận:** Tự động đếm số lượng, phân bổ tỷ lệ Nhận biết - Thông hiểu - Vận dụng, xử lý mượt mà công thức phức tạp.
    *   **Xây dựng Kế hoạch bài dạy:** Bám sát chuẩn cấu trúc Công văn 5512, tích hợp dễ dàng Năng lực số (Thông tư 18) và Dạy học hòa nhập.
    
    👈 *Vui lòng chọn chức năng tại thanh menu bên trái để bắt đầu.*
    """)
    
elif menu_selection == "📘 Xây dựng KHBD (Giáo án)":
    render_khbd_ui(is_ai_enabled)
    
elif menu_selection == "📄 Tạo Đề & Ma trận":
    render_exam_ui(is_ai_enabled)
    
elif menu_selection == "⚙️ Cấu hình AI":
    st.markdown("## ⚙️ Cấu hình API Key (Thủ công)")
    st.info("Nếu hệ thống của bạn đã được cấu hình sẵn biến môi trường (Secrets) bởi Quản trị viên, bạn **không cần** nhập lại tại đây.")
    
    if st.session_state.get('is_vip'):
        st.success("🎉 Hệ thống đã tự động nhận diện khóa API của Quản trị viên. Bạn đang sử dụng toàn bộ tính năng VIP ở tốc độ cao nhất!")
    else:
        api_input = st.text_input("Nhập Gemini API Key của bạn:", type="password", value=st.session_state.get('api_key_value', ''))
        if st.button("💾 Lưu Cấu Hình", type="primary"):
            if api_input.strip():
                st.session_state['api_key_value'] = api_input.strip()
                st.session_state['has_api_key'] = True
                st.success("Đã lưu API Key thành công! Hãy chuyển sang các tab chức năng để sử dụng.")
                st.rerun()
            else:
                st.session_state['has_api_key'] = False
                st.error("Vui lòng nhập API Key hợp lệ.")
