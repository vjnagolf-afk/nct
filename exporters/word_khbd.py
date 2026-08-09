# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/export_word.py
Nhiệm vụ: Bộ điều phối trung tâm kết xuất Markdown / AI Generated Content 
thành file Word (.docx) chuẩn 5512 (Bản Kỹ sư trưởng tối ưu toàn diện).
============================================================
"""

import io
import re
import json
import logging
import streamlit as st
from typing import List, Dict, Any, Optional

import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

logger = logging.getLogger(__name__)

try:
    from .markdown_tokenizer import MarkdownTokenizer
except ImportError:
    try:
        from export.markdown_tokenizer import MarkdownTokenizer
    except ImportError:
        MarkdownTokenizer = None

try:
    from .word_math import insert_math_to_paragraph
except ImportError:
    try:
        from export.word_math import insert_math_to_paragraph
    except ImportError:
        insert_math_to_paragraph = None

try:
    from .word_tables import process_and_draw_markdown_table
except ImportError:
    try:
        from export.word_tables import process_and_draw_markdown_table
    except ImportError:
        process_and_draw_markdown_table = None

try:
    from .word_images import insert_image_to_paragraph, insert_image_to_docx
except ImportError:
    try:
        from export.word_images import insert_image_to_paragraph, insert_image_to_docx
    except ImportError:
        insert_image_to_paragraph = None
        insert_image_to_docx = None


class ScienceNormalizer:
    """Bộ lọc chuẩn hóa khoa học (Toán, Lý, Hóa) chống cắt cụt dấu căn và ký hiệu"""
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    MAP = {
        r'\perp': '⊥', r'\circ': '°', r'\ne': '≠', r'\le': '≤', r'\ge': '≥', 
        r'\times': '×', r'\div': '÷', r'\triangle': '△', r'\angle': '∠', 
        r'\rightarrow': '→', r'\Rightarrow': '⇒', r'\approx': '≈',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\pi': 'π', 
        r'\sum': '∑', r'\int': '∫', r'\sqrt': '√'
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text: 
            return ""
        # Làm sạch ký hiệu LaTeX thô để chuyển về dạng văn bản Unicode rõ nét không bị cắt cụt
        text = str(text).replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        
        # Xử lý căn thức toàn diện tránh mất nét
        text = re.sub(r'\\sqrt\s*\{([\s\S]+?)\}', r'√(\1)', text)
        text = re.sub(r'\\sqrt\s*([a-zA-Z0-9]+)', r'√\1', text)
        
        # Xử lý phân số
        while r'\frac{' in text:
            text = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'((\1)/(\2))', text)
            
        # Dịch chuyển chỉ số trên, chỉ số dưới
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        text = re.sub(r'([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)\^(\d*[+\-])', lambda m: m.group(1) + m.group(2).translate(cls.SUP), text)
        
        for k, v in cls.MAP.items(): 
            text = text.replace(k, v)
            
        return re.sub(r'\\text\{([\s\S]+?)\}', r'\1', text)


class WordExportEngine:

    @staticmethod
    def _set_font(run, font_name="Times New Roman"):
        """Khóa cứng định dạng Font XML an toàn không sinh thẻ trùng lặp"""
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
    def _set_shading(p_or_cell, color_hex):
        element = p_or_cell._element.get_or_add_pPr() if hasattr(p_or_cell, 'paragraphs') else p_or_cell._element.get_or_add_tcPr()
        shd = element.find(qn("w:shd"))
        if shd is None: 
            shd = OxmlElement("w:shd")
            element.append(shd)
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), color_hex)

    @classmethod
    def _render_inline(cls, p, tokens: List[Dict[str, Any]], data_cache: dict = None):
        if not tokens: 
            return
        for t in tokens:
            tt = t.get("type")
            c = t.get("content", "") or t.get("text", "")
            
            if tt in ["text", "bold", "italic", "underline", "strike", "highlight", "subscript", "superscript", "inline_code"]:
                run = p.add_run(c)
                cls._set_font(run, "Courier New" if tt == "inline_code" else "Times New Roman")
                run.font.size = Pt(13)
                
                if tt == "bold": 
                    run.bold = True
                elif tt == "italic": 
                    run.italic = True
                elif tt == "underline": 
                    run.underline = True
                elif tt == "strike": 
                    run.font.strike = True
                elif tt == "subscript": 
                    run.font.subscript = True
                elif tt == "superscript": 
                    run.font.superscript = True
                elif tt == "highlight": 
                    run.font.highlight_color = 4
                elif tt == "inline_code": 
                    run.font.size = Pt(11)
                    run.font.color.rgb = RGBColor(199, 37, 78)
                    
            elif tt in ["inline_math", "math_inline", "math"]:
                normalized_math = ScienceNormalizer.normalize(c)
                run = p.add_run(normalized_math)
                run.font.italic = True
                cls._set_font(run, "Times New Roman")
                
            elif tt == "image":
                img_id = c.strip()
                img_src = None
                if data_cache and "pages" in data_cache:
                    for page in data_cache["pages"]:
                        for img in page.get("images", []):
                            if img.get("id") == img_id:
                                img_src = {"base64": img.get("base64"), "caption": img_id}
                                break
                        if img_src: 
                            break
                            
                if insert_image_to_paragraph:
                    if img_src:
                        insert_image_to_paragraph(p, img_src)
                    else:
                        insert_image_to_paragraph(p, img_id)
                else:
                    run_img = p.add_run(f"[Hình ảnh: {img_id}]")
                    run_img.italic = True
            else:
                run = p.add_run(str(c))
                cls._set_font(run, "Times New Roman")
                run.font.size = Pt(13)

    @classmethod
    def convert_markdown_to_docx_bytes(cls, markdown_text: str, metadata: dict = None) -> bytes:
        doc = Document()
        
        # Thiết lập chuẩn trang A4 hành chính giáo dục
        for s in doc.sections:
            s.page_height, s.page_width = Inches(11.69), Inches(8.27)
            s.top_margin, s.bottom_margin, s.right_margin = Inches(0.79), Inches(0.79), Inches(0.79)
            s.left_margin = Inches(1.18) # Lề trái 3cm đóng ghim giáo án

        ns = doc.styles['Normal']
        ns.font.name, ns.font.size = 'Times New Roman', Pt(13)
        ns.paragraph_format.space_after = Pt(6)

        # Sử dụng MarkdownTokenizer nếu có sẵn, nếu không sẽ gọi fallback
        if MarkdownTokenizer and hasattr(MarkdownTokenizer, 'parse'):
            try:
                ast_nodes = MarkdownTokenizer.parse(markdown_text)
            except Exception:
                ast_nodes = [{"type": "paragraph", "tokens": [{"type": "text", "content": markdown_text}]}]
        else:
            ast_nodes = [{"type": "paragraph", "tokens": [{"type": "text", "content": markdown_text}]}]

        for node in ast_nodes:
            nt = node.get("type")
            
            if nt == "paragraph":
                p = doc.add_paragraph()
                cls._render_inline(p, node.get("tokens", []), metadata)
                
            elif nt == "heading":
                lv = min(max(node.get("level", 1), 1), 3)
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                if lv == 1: 
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cls._render_inline(p, node.get("tokens", []), metadata)
                for r in p.runs: 
                    r.bold = True
                    r.font.size = Pt(17 - lv)
                    cls._set_font(r)
                    
            elif nt == "list_item":
                st = 'List Number' if node.get("style") == "number" else 'List Bullet'
                p = doc.add_paragraph(style=st)
                p.paragraph_format.left_indent = Inches(0.25 * node.get("level", 1) + 0.25)
                p.paragraph_format.first_line_indent = Inches(-0.25)
                cls._render_inline(p, node.get("tokens", []), metadata)
                
            elif nt == "checkbox":
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25 * node.get("level", 1))
                r = p.add_run("☑ " if node.get("checked") else "☐ ")
                cls._set_font(r, "MS Gothic")
                r.bold = True
                cls._render_inline(p, node.get("tokens", []), metadata)
                
            elif nt == "code":
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                cls._set_shading(p, "F5F5F5")
                r = p.add_run(node.get("text", ""))
                r.font.size = Pt(10.5)
                cls._set_font(r, "Courier New")
                
            elif nt == "hr":
                p = doc.add_paragraph()
                pPr = p._element.get_or_add_pPr()
                pb = OxmlElement("w:pBdr")
                bottom = OxmlElement("w:bottom")
                bottom.set(qn("w:val"), "single")
                bottom.set(qn("w:sz"), "8")
                bottom.set(qn("w:color"), "CCCCCC")
                pb.append(bottom)
                pPr.append(pb)
                
            elif nt == "page_break":
                doc.add_page_break()
                
            elif nt == "table":
                rows, headers, cols = node.get("rows", []), node.get("headers", []), node.get("cols", 1)
                if cols > 0:
                    table = doc.add_table(rows=len(rows) + (1 if headers else 0), cols=cols)
                    table.style = 'Table Grid'
                    table.alignment = 1
                    r_idx = 0
                    if headers:
                        h_row = table.rows[0]
                        h_row._element.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
                        for c_idx, cell_n in enumerate(headers):
                            cell = h_row.cells[c_idx]
                            cls._set_shading(cell, "EAEAEA")
                            p = cell.paragraphs[0]
                            cls._render_inline(p, cell_n.get("content", []), metadata)
                            for r in p.runs: 
                                r.bold = True
                        r_idx = 1
                    for loop_idx, r_data in enumerate(rows):
                        row = table.rows[r_idx]
                        row._element.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                        bg = "F9F9F9" if loop_idx % 2 == 1 else "FFFFFF"
                        for c_idx, cell_n in enumerate(r_data):
                            if c_idx < len(row.cells):
                                cell = row.cells[c_idx]
                                cls._set_shading(cell, bg)
                                cls._render_inline(cell.paragraphs[0], cell_n.get("content", []), metadata)
                        r_idx += 1
                    for row in table.rows:
                        for cell in row.cells: 
                            cell.width = Inches(6.3 / cols)

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        metadata = {}
        if isinstance(data_cache, dict):
            metadata = data_cache.copy()
            md_text = metadata.get("ai_generated_content", "")
        else:
            md_text = str(data_cache)
            
        if "current_source_metadata" in st.session_state:
            metadata["pages"] = st.session_state["current_source_metadata"].get("pages", [])
            
        return cls.convert_markdown_to_docx_bytes(md_text, metadata=metadata)


def export_word(markdown_text_or_cache) -> bytes:
    try:
        metadata = {}
        if isinstance(markdown_text_or_cache, dict):
            metadata = markdown_text_or_cache.copy()
            md_text = metadata.get("ai_generated_content", "")
        else:
            md_text = str(markdown_text_or_cache)
            
        if "current_source_metadata" in st.session_state:
            metadata["pages"] = st.session_state["current_source_metadata"].get("pages", [])
            
        return WordExportEngine.convert_markdown_to_docx_bytes(md_text, metadata=metadata)
        
    except Exception as fatal_err:
        fallback_doc = Document()
        fallback_doc.add_paragraph("KẾ HOẠCH BÀI DẠY (BẢN PHỤC HỒI)")
        fallback_doc.add_paragraph(f"Lỗi: {fatal_err}")
        bio = io.BytesIO()
        fallback_doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
