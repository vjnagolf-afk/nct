import io
import docx
import PyPDF2

class DocumentProcessor:
    """Class chịu trách nhiệm xử lý các luồng tài liệu đầu vào (PDF/Word)."""
    
    @staticmethod
    def read_docx(file_bytes: bytes) -> str:
        """Đọc và trích xuất text từ file Word (.docx)"""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
            return "\n".join(text)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file Word: {str(e)}")

    @staticmethod
    def read_pdf(file_bytes: bytes) -> str:
        """Đọc và trích xuất text từ file PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text_content = []
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text_content.append(extracted_text)
            return "\n".join(text_content)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file PDF: {str(e)}")

    @classmethod
    def process_uploaded_file(cls, uploaded_file) -> str:
        """
        Hàm trung tâm: Nhận file từ giao diện Streamlit (st.file_uploader)
        và trả về toàn bộ nội dung dạng chuỗi văn bản (String).
        """
        if uploaded_file is None:
            return ""
            
        file_extension = uploaded_file.name.split('.')[-1].lower()
        file_bytes = uploaded_file.read() # Đọc file dưới dạng byte stream
        
        if file_extension == 'docx':
            return cls.read_docx(file_bytes)
        elif file_extension == 'pdf':
            return cls.read_pdf(file_bytes)
        else:
            raise ValueError(f"Định dạng .{file_extension} chưa được hỗ trợ. Vui lòng dùng PDF hoặc DOCX.")
