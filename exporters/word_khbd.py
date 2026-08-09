# exporters/word_khbd.py
import io
import docx

class KhbdWordExporter:
    @staticmethod
    def replace_text_in_paragraph(paragraph, key, value):
        placeholder = f"{{{{{key}}}}}"
        if placeholder in paragraph.text:
            # Nếu giá trị có chứa ký tự xuống dòng, ta xử lý tách đoạn sạch sẽ
            if "\n" in str(value):
                lines = str(value).split("\n")
                paragraph.text = lines[0]
                for line in lines[1:]:
                    paragraph.insert_paragraph_before(line)
            else:
                paragraph.text = paragraph.text.replace(placeholder, str(value))

    @staticmethod
    def export_khbd(khbd_data: dict, template_path: str = "templates/word/mau_khbd_5512.docx") -> bytes:
        try:
            doc = docx.Document(template_path)
        except Exception:
            raise ValueError(f"Không tìm thấy file mẫu tại {template_path}. Hãy chắc chắn thư mục templates/word/ chứa file mau_khbd_5512.docx")
            
        # Thay thế trong các đoạn văn bản chính
        for p in list(doc.paragraphs):
            for key, value in khbd_data.items():
                KhbdWordExporter.replace_text_in_paragraph(p, key, value)
                
        # Thay thế trong bảng biểu
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in list(cell.paragraphs):
                        for key, value in khbd_data.items():
                            KhbdWordExporter.replace_text_in_paragraph(p, key, value)

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.getvalue()
