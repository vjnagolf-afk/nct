# -*- coding: utf-8 -*-
"""
============================================================
MODULE: exporters/word_khbd.py
Nhiệm vụ: Kết xuất Word giáo án 5512 phẳng, sửa lỗi font toán và lỗi tràn dòng template.
============================================================
"""

import io
import re
import docx
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from typing import Any  # ĐÃ SỬA: Bổ sung import Any bị thiếu gây sập code trước đó

class ScienceNormalizer:
    """Bộ lọc chuẩn hóa ký hiệu toán học nâng cao sang Unicode chuẩn của Word"""
    MAP = {
        r'\sqrt': '√', r'\pm': '±', r'\ge': '≥', r'\le': '≤', r'\ne': '≠',
        r'\times': '×', r'\div': '÷', r'\alpha': 'α', r'\beta': 'β',
        r'\gamma': 'γ', r'\pi': 'π', r'\Delta': 'Δ', r'\rightarrow': '→',
        r'\Rightarrow': '⇒', r'\Leftrightarrow': '⇔', r'\approx': '≈'
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text: 
            return ""
        text = str(text)
        # Loại bỏ các ký tự bọc LaTeX thô tránh gây rối mắt cho giáo viên trên bản Word
        text = text.replace('$', '').replace(r'\(', '').replace(r'\)', '')
        
        # Xử lý các mã căn thức phổ biến
        text = re.sub(r'\\sqrt\s*\{([\s\S]+?)\}', r'√(\1)', text)
        text = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'(\1 / \2)', text)
        
        for k, v in cls.MAP.items(): 
            text = text.replace(k, v)
        return text


class KhbdWordExporter:
    @staticmethod
    def _set_font(run, font_name="Times New Roman", size_pt=12):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        try:
            rPr = run._element.get_or_add_rPr()
            rFonts = rPr.find(qn("w:rFonts"))
            if rFonts is None:
                rFonts = OxmlElement("w:rFonts")
                rPr.append(rFonts)
            rFonts.set(qn('w:ascii'), font_name)
            rFonts.set(qn('w:hAnsi'), font_name)
            rFonts.set(qn('w:cs'), font_name)
        except Exception:
            pass

    @classmethod
    def replace_text_in_paragraph(cls, paragraph, key, value):
        placeholder = f"{{{{{key}}}}}"
        if placeholder in paragraph.text:
            cleaned_value = ScienceNormalizer.normalize(str(value))
            # ĐÃ SỬA: Thay vì chèn đè paragraph làm hỏng bảng biểu template, ta thực hiện thay thế nội dung text trực tiếp trong run
            paragraph.text = paragraph.text.replace(placeholder, cleaned_value)
            for run in paragraph.runs:
                cls._set_font(run)

    @classmethod
    def export_khbd(cls, khbd_data: dict, template_path: str = "templates/word/mau_khbd_5512.docx") -> bytes:
        try:
            doc = docx.Document(template_path)
        except Exception:
            doc = docx.Document()
            for s in doc.sections:
                s.top_margin, s.bottom_margin = Inches(0.79), Inches(0.79)
                s.left_margin, s.right_margin = Inches(1.18), Inches(0.79)
            
        # Duyệt qua toàn bộ văn bản gốc bên ngoài bảng
        for p in list(doc.paragraphs):
            for key, value in khbd_data.items():
                cls.replace_text_in_paragraph(p, key, value)
                
        # Duyệt sâu vào tất cả các ô trong bảng biểu mẫu 5512 để đổ text
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
    def export_to_word(cls, data_cache: Any) -> bytes:
        if isinstance(data_cache, dict):
            # Nếu có data trích xuất phẳng sẵn sàng thì ưu tiên map trực tiếp vào template mẫu chuẩn 5512
            if "CHU_DE" in data_cache or any(k in data_cache for k in ["MUC_TIEU", "NOI_DUNG"]):
                return cls.export_khbd(data_cache)
                
            content = data_cache.get("ai_generated_content", "")
            if content:
                doc = Document()
                for line in content.split("\n"):
                    p = doc.add_paragraph()
                    r = p.add_run(ScienceNormalizer.normalize(line))
                    cls._set_font(r)
                bio = io.BytesIO()
                doc.save(bio)
                bio.seek(0)
                return bio.getvalue()
        return cls.export_khbd(dict(data_cache))
