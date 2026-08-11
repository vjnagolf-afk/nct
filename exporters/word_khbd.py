# -*- coding: utf-8 -*-
"""
============================================================
MODULE: exporters/word_khbd.py
Nhiệm vụ: Điền cấu trúc JSON phẳng vào Template Word 5512,
xử lý dứt điểm "ảo giác" công thức Toán học / v(x) / SQRT.
============================================================
"""

import io
import re
import json
import docx

class ScienceNormalizer:
    """Bộ lọc chuẩn hóa khoa học, chống cắt cụt dấu căn và ép chuẩn ký hiệu bị ảo giác"""
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    MAP = {
        r'\perp': '⊥', r'\circ': '°', r'\ne': '≠', r'\le': '≤', r'\ge': '≥', 
        r'\times': '×', r'\div': '÷', r'\triangle': '△', r'\angle': '∠', 
        r'\rightarrow': '→', r'\Rightarrow': '⇒', r'\approx': '≈',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\pi': 'π', 
        r'\sum': '∑', r'\int': '∫'
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text: 
            return ""
        
        text = str(text).replace('$', '').strip()
        
        # Xử lý các từ khóa ảo giác của AI: SQRT(x), sqrt(x), v(x), V(x)
        text = re.sub(r'(?i)sqrt\s*\(([^)]+)\)', r'√(\1)', text)
        text = re.sub(r'\bv\(([^)]+)\)', r'√(\1)', text)
        text = re.sub(r'\bV\(([^)]+)\)', r'√(\1)', text)
        
        # Xử lý LaTeX chuẩn \sqrt{}
        text = re.sub(r'\\sqrt\s*\{([\s\S]+?)\}', r'√(\1)', text)
        text = re.sub(r'\\sqrt\s*([a-zA-Z0-9]+)', r'√\1', text)
        
        # Phân số LaTeX
        while r'\frac{' in text:
            text = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'(\1)/(\2)', text)
            
        # Chỉ số trên dưới
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        text = re.sub(r'([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)\^(\d*[+\-])', lambda m: m.group(1) + m.group(2).translate(cls.SUP), text)
        
        for k, v in cls.MAP.items(): 
            text = text.replace(k, v)
        return text

class KhbdWordExporter:
    @staticmethod
    def replace_text_in_paragraph(paragraph, key, value):
        placeholder = f"{{{{{key}}}}}"
        if placeholder in paragraph.text:
            cleaned_value = ScienceNormalizer.normalize(str(value))
            
            # Tách dòng an toàn giữ nguyên Style của Word
            if "\n" in cleaned_value:
                lines = cleaned_value.split("\n")
                paragraph.text = paragraph.text.replace(placeholder, lines[0])
                for line in lines[1:]:
                    new_p = paragraph.insert_paragraph_before(line)
                    new_p.style = paragraph.style
            else:
                paragraph.text = paragraph.text.replace(placeholder, cleaned_value)

    @classmethod
    def export_khbd(cls, khbd_data: dict, template_path: str = "templates/word/mau_khbd_5512.docx") -> bytes:
        try:
            doc = docx.Document(template_path)
        except Exception:
            # Fallback an toàn nếu mất file mẫu
            doc = docx.Document()
            doc.add_paragraph("LỖI HỆ THỐNG: Không tìm thấy file mẫu tại đường dẫn 'templates/word/mau_khbd_5512.docx'")
            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()
            
        # Điền biến vào văn bản
        for p in list(doc.paragraphs):
            for key, value in khbd_data.items():
                cls.replace_text_in_paragraph(p, key, value)
                
        # Điền biến vào bảng biểu
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in list(cell.paragraphs):
                        for key, value in khbd_data.items():
                            cls.replace_text_in_paragraph(p, key, value)

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.getvalue()

    @classmethod
    def export_to_word(cls, data_cache) -> bytes:
        if isinstance(data_cache, dict):
            ai_content = data_cache.get("ai_generated_content", "")
            try:
                # Ép chuỗi AI sinh ra thành chuẩn JSON Dictionary
                json_data = json.loads(ai_content) if isinstance(ai_content, str) else ai_content
                return cls.export_khbd(json_data)
            except json.JSONDecodeError:
                pass
        return b""

def export_word(data_cache) -> bytes:
    return KhbdWordExporter.export_to_word(data_cache)
