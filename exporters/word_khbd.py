# -*- coding: utf-8 -*-
"""
============================================================
MODULE: exporters/word_khbd.py
Nhiệm vụ: Động cơ kết xuất Word chuẩn 5512, tích hợp ScienceNormalizer 
chống lỗi công thức toán, lý, hóa.
============================================================
"""

import io
import re
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class ScienceNormalizer:
    """Bộ lọc chuẩn hóa khoa học (Toán, Lý, Hóa) chống cắt cụt dấu căn và ký hiệu"""
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
        text = str(text).replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        text = re.sub(r'\\sqrt\s*\{([\s\S]+?)\}', r'√( \1 )', text)
        text = re.sub(r'\\sqrt\s*([a-zA-Z0-9]+)', r'√\1', text)
        while r'\frac{' in text:
            text = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'( \1 / \2 )', text)
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        text = re.sub(r'([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)\^(\d*[+\-])', lambda m: m.group(1) + m.group(2).translate(cls.SUP), text)
        for k, v in cls.MAP.items(): 
            text = text.replace(k, v)
        return re.sub(r'\\text\{([\s\S]+?)\}', r'\1', text)


class KhbdWordExporter:
    @staticmethod
    def _set_font(run, font_name="Times New Roman"):
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

    @staticmethod
    def replace_text_in_paragraph(paragraph, key, value):
        placeholder = f"{{{{{key}}}}}"
        if placeholder in paragraph.text:
            cleaned_value = ScienceNormalizer.normalize(str(value))
            if "\n" in cleaned_value:
                lines = cleaned_value.split("\n")
                paragraph.text = lines[0]
                for line in lines[1:]:
                    paragraph.insert_paragraph_before(line)
            else:
                paragraph.text = paragraph.text.replace(placeholder, cleaned_value)

    @classmethod
    def export_khbd(cls, khbd_data: dict, template_path: str = "templates/word/mau_khbd_5512.docx") -> bytes:
        try:
            doc = docx.Document(template_path)
        except Exception:
            doc = docx.Document()
            for s in doc.sections:
                s.top_margin, s.bottom_margin = Inches(0.79), Inches(0.79)
                s.left_margin, s.right_margin = Inches(1.18), Inches(0.79)
            
        for p in list(doc.paragraphs):
            for key, value in khbd_data.items():
                cls.replace_text_in_paragraph(p, key, value)
                
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
        """Hỗ trợ linh hoạt kết xuất từ Markdown text hoặc từ Dictionary dữ liệu"""
        if isinstance(data_cache, dict):
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
            return cls.export_khbd(data_cache)
        else:
            doc = Document()
            p = doc.add_paragraph()
            r = p.add_run(ScienceNormalizer.normalize(str(data_cache)))
            cls._set_font(r)
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            return bio.getvalue()
