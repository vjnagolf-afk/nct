import io
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class KhbdWordExporter:
    """
    Trình kết xuất Kế hoạch bài dạy ra file Word chuẩn 5512.
    Nhận dữ liệu Dictionary/JSON đã được xác thực từ KhbdEngine.
    """
    
    @staticmethod
    def _setup_document() -> docx.Document:
        doc = docx.Document()
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        return doc

    @staticmethod
    def export_khbd(khbd_data: dict) -> bytes:
        doc = KhbdWordExporter._setup_document()
        
        tieu_de = khbd_data.get("tieu_de", "KẾ HOẠCH BÀI DẠY")
        muc_tieu = khbd_data.get("muc_tieu", {})
        thiet_bi = khbd_data.get("thiet_bi", "")
        tien_trinh = khbd_data.get("tien_trinh", [])
        tong_thoi_gian = khbd_data.get("tong_thoi_gian_phut", 0)

        # TIÊU ĐỀ CHÍNH
        title = doc.add_heading(tieu_de.upper(), level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"(Tổng thời lượng dự kiến: {tong_thoi_gian} phút)").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()

        # I. MỤC TIÊU
        doc.add_heading("I. MỤC TIÊU", level=2)
        
        p_kt = doc.add_paragraph()
        p_kt.add_run("1. Kiến thức: ").bold = True
        for kt in muc_tieu.get("kien_thuc", []):
            doc.add_paragraph(f"- {kt}", style='List Bullet')
            
        p_nl = doc.add_paragraph()
        p_nl.add_run("2. Năng lực: ").bold = True
        for nl in muc_tieu.get("nang_luc", []):
            doc.add_paragraph(f"- {nl}", style='List Bullet')
            
        p_pc = doc.add_paragraph()
        p_pc.add_run("3. Phẩm chất: ").bold = True
        for pc in muc_tieu.get("pham_chat", []):
            doc.add_paragraph(f"- {pc}", style='List Bullet')

        # II. THIẾT BỊ DẠY HỌC
        doc.add_heading("II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU", level=2)
        doc.add_paragraph(thiet_bi)

        # III. TIẾN TRÌNH DẠY HỌC
        doc.add_heading("III. TIẾN TRÌNH DẠY HỌC", level=2)
        
        for index, hd in enumerate(tien_trinh, 1):
            ten_hd = hd.get("ten_hoat_dong", f"Hoạt động {index}")
            thoi_gian = hd.get("thoi_gian_du_kien", 0)
            
            # Tên hoạt động
            p_hd = doc.add_paragraph()
            p_hd.add_run(f"Hoạt động {index}: {ten_hd} ({thoi_gian} phút)").bold = True
            
            # a) Mục tiêu
            p_mt = doc.add_paragraph()
            p_mt.add_run("a) Mục tiêu: ").bold = True
            p_mt.add_run(hd.get("muc_tieu", ""))
            
            # b) Nội dung
            p_nd = doc.add_paragraph()
            p_nd.add_run("b) Nội dung: ").bold = True
            p_nd.add_run(hd.get("noi_dung", ""))
            
            # c) Sản phẩm
            p_sp = doc.add_paragraph()
            p_sp.add_run("c) Sản phẩm: ").bold = True
            p_sp.add_run(hd.get("san_pham", ""))
            
            # d) Tổ chức thực hiện
            p_tc = doc.add_paragraph()
            p_tc.add_run("d) Tổ chức thực hiện: ").bold = True
            doc.add_paragraph(hd.get("to_chuc_thuc_hien", ""))
            
            doc.add_paragraph() 

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.getvalue()
