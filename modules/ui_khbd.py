# 6. HIỂN THỊ KẾT QUẢ & XUẤT WORD
    if 'khbd_data_clean' in st.session_state:
        khbd_data = st.session_state['khbd_data_clean']
        st.markdown("### 📊 Kết quả Kế hoạch bài dạy (Chuẩn 5512)")
        
        # --- THÊM PHẦN PREVIEW TRỰC QUAN ---
        with st.container(border=True):
            st.markdown(f"#### 🏷️ BÀI: {khbd_data.get('TEN_BAI_HOC', '')}")
            st.info(f"**Mục tiêu kiến thức:**\n{khbd_data.get('MUC_TIEU_KIEN_THUC', '')}")
            
            tab1, tab2, tab3, tab4 = st.tabs(["Khởi động", "Hình thành KT", "Luyện tập", "Vận dụng"])
            with tab1:
                st.write("**Nội dung:**\n", khbd_data.get('NOI_DUNG', ''))
                st.write("**Chuyển giao NV:**\n", khbd_data.get('CHUYEN_GIAO_NHIEM_VU_HOC_TAP', ''))
            with tab2:
                st.write("**Nội dung 2.1:**\n", khbd_data.get('HD1_NOI_DUNG', ''))
            with tab3:
                st.write("**Nội dung luyện tập:**\n", khbd_data.get('LT_NOI_DUNG', ''))
            with tab4:
                st.write("**Vận dụng:**\n", khbd_data.get('VD_NOI_DUNG', ''))
        # ------------------------------------

        col_down, col_del = st.columns(2)
        with col_down:
            try:
                word_bytes = KhbdWordExporter.export_khbd(khbd_data)
                st.download_button(
                    label="📥 TẢI FILE WORD ĐÚNG CHUẨN MẪU TẢI LÊN",
                    data=word_bytes,
                    file_name=f"KHBD_{ten_bai.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(str(e))
                
        with col_del:
            if st.button("🗑️ Xóa kết quả làm lại", use_container_width=True):
                del st.session_state['khbd_data_clean']
                st.rerun()
