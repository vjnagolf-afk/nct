# exporters/word_khbd.py
import io
import re
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class ScienceNormalizer:
    """Bộ chuyển đổi ký hiệu khoa học (Toán, Lý, Hóa) sang chuẩn văn bản sạch"""
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    MAP = {
        r'\perp': '⊥', r'\circ': '°', r'\ne': '≠', r'\le': '≤', r'\ge': '≥', 
        r'\times': '×', r'\div': '÷', r'\triangle': '△', r'\angle': '∠', 
        r'\rightarrow': '→', r'\Rightarrow': '⇒', r'\approx': '≈',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\pi': 'π', r'\sum': '∑', r'\int': '∫'
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text: return ""
        text = str(text).replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        # Xử lý phân số thô phẳng
        while r'\frac{' in text:
            text = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'((\1)/(\2))', text)
        text = re.sub(r'\\sqrt\{([\s\S]+?)\}', r'√(\1)', text)
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        text = re.sub(r'([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)\^(\d*[+\-])', lambda m: m.group(1) + m.group(2).translate(cls.SUP), text)
        for k, v in cls.MAP.items(): text = text.replace(k, v)
        return re.sub(r'\\text\{([\s\S]+?)\}', r'\1', text)

class KhbdWordExporter:
    @staticmethod
    def _set_font(run, font_name="Times New Roman"):
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)

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

    @staticmethod
    def export_khbd(khbd_data: dict, template_path: str = "templates/word/mau_khbd_5512.docx") -> bytes:
        try:
            doc = docx.Document(template_path)
        except Exception:
            # Fallback nếu chưa có file mẫu, tự động tạo mới tài liệu chuẩn A4
            doc = docx.Document()
            for s in doc.sections:
                s.top_margin, s.bottom_margin = Inches(0.79), Inches(0.79)
                s.left_margin, s.right_margin = Inches(1.18), Inches(0.79)
            
        # Thay thế trong văn bản thường
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
