import io
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

class ExamWordExporter:
    """
    Trình kết xuất Đề thi và Ma trận ra file Word.
    Nhận dữ liệu Dictionary/JSON đã được xác thực từ ExamEngine.
    """
    
    @staticmethod
    def _setup_document() -> docx.Document:
        """Cấu hình font chữ và lề chuẩn"""
        doc = docx.Document()
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        return doc

    @staticmethod
    def export_exam_and_matrix(exam_data: dict) -> bytes:
        """
        Hàm chính xuất ra file .docx
        Bao gồm: Phần 1 (Ma trận), Phần 2 (Đề thi), Phần 3 (Đáp án)
        """
        doc = ExamWordExporter._setup_document()
        
        tieu_de = exam_data.get("tieu_de", "ĐỀ KIỂM TRA ĐÁNH GIÁ")
        danh_sach_cau_hoi = exam_data.get("danh_sach_cau_hoi", [])
        ma_tran = exam_data.get("ma_tran", {})

        # ==========================================
        # PHẦN 1: IN BẢNG MA TRẬN
        # ==========================================
        heading = doc.add_heading("I. MA TRẬN ĐỀ KIỂM TRA", level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Tạo bảng cơ bản (Python xử lý cấu trúc, không phải AI)
        chu_de_dict = ma_tran.get("chi_tiet_chu_de", {})
        so_chu_de = len(chu_de_dict)
        
        # Bảng gồm: Chủ đề | Nhận biết | Thông hiểu | Vận dụng | Vận dụng cao | Tổng
        table = doc.add_table(rows=1, cols=6)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Chủ đề / Kiến thức'
        hdr_cells[1].text = 'Nhận biết'
        hdr_cells[2].text = 'Thông hiểu'
        hdr_cells[3].text = 'Vận dụng'
        hdr_cells[4].text = 'Vận dụng cao'
        hdr_cells[5].text = 'Tổng số câu'

        for ten_cd, muc_do_data in chu_de_dict.items():
            row_cells = table.add_row().cells
            row_cells[0].text = ten_cd
            
            # Đếm trắc nghiệm (TN) và Tự luận (TL) từ JSON
            nb_tn = muc_do_data.get("nhan_biet", {}).get("trac_nghiem", 0)
            nb_tl = muc_do_data.get("nhan_biet", {}).get("tu_luan", 0)
            row_cells[1].text = f"TN:{nb_tn} | TL:{nb_tl}" if (nb_tn or nb_tl) else ""
            
            th_tn = muc_do_data.get("thong_hieu", {}).get("trac_nghiem", 0)
            th_tl = muc_do_data.get("thong_hieu", {}).get("tu_luan", 0)
            row_cells[2].text = f"TN:{th_tn} | TL:{th_tl}" if (th_tn or th_tl) else ""
            
            vd_tn = muc_do_data.get("van_dung", {}).get("trac_nghiem", 0)
            vd_tl = muc_do_data.get("van_dung", {}).get("tu_luan", 0)
            row_cells[3].text = f"TN:{vd_tn} | TL:{vd_tl}" if (vd_tn or vd_tl) else ""
            
            vdc_tn = muc_do_data.get("van_dung_cao", {}).get("trac_nghiem", 0)
            vdc_tl = muc_do_data.get("van_dung_cao", {}).get("tu_luan", 0)
            row_cells[4].text = f"TN:{vdc_tn} | TL:{vdc_tl}" if (vdc_tn or vdc_tl) else ""
            
            tong_cau = nb_tn + nb_tl + th_tn + th_tl + vd_tn + vd_tl + vdc_tn + vdc_tl
            row_cells[5].text = str(tong_cau)

        doc.add_page_break()

        # ==========================================
        # PHẦN 2: IN ĐỀ KIỂM TRA
        # ==========================================
        heading = doc.add_heading(tieu_de, level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        trac_nghiem = [c for c in danh_sach_cau_hoi if c["loai_cau_hoi"] == "trac_nghiem"]
        tu_luan = [c for c in danh_sach_cau_hoi if c["loai_cau_hoi"] == "tu_luan"]

        if trac_nghiem:
            doc.add_heading("A. PHẦN TRẮC NGHIỆM", level=2)
            for idx, cau in enumerate(trac_nghiem, 1):
                doc.add_paragraph(f"Câu {idx}: {cau['noi_dung_cau_hoi']}")
                dap_an_list = cau.get("danh_sach_dap_an", [])
                if dap_an_list:
                    p = doc.add_paragraph()
                    for da in dap_an_list:
                        p.add_run(f"{da['nhan']}. {da['noi_dung']}    ")

        if tu_luan:
            doc.add_heading("B. PHẦN TỰ LUẬN", level=2)
            for idx, cau in enumerate(tu_luan, 1):
                doc.add_paragraph(f"Câu {idx}: {cau['noi_dung_cau_hoi']}")
                doc.add_paragraph("") # Khoảng trống làm bài

        doc.add_page_break()

        # ==========================================
        # PHẦN 3: ĐÁP ÁN & HƯỚNG DẪN GIẢI
        # ==========================================
        heading = doc.add_heading("HƯỚNG DẪN CHẤM & ĐÁP ÁN", level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if trac_nghiem:
            doc.add_heading("A. Trắc nghiệm", level=2)
            da_tn_text = " | ".join([f"Câu {idx+1}: {cau['dap_an_dung']}" for idx, cau in enumerate(trac_nghiem)])
            doc.add_paragraph(da_tn_text)

        if tu_luan:
            doc.add_heading("B. Tự luận", level=2)
            for idx, cau in enumerate(tu_luan, 1):
                p = doc.add_paragraph(f"Câu {idx}: ")
                p.runs[0].bold = True
                doc.add_paragraph(f"{cau['huong_dan_giai']}")

        # Lưu file
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.getvalue()
