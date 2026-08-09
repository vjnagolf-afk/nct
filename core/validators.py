# -*- coding: utf-8 -*-
"""
============================================================
MODULE: core/validators.py
Nhiệm vụ: Kiểm tra, làm sạch và tự động vá lỗi cú pháp JSON 
do LLM sinh ra trước khi đưa vào hệ thống xử lý.
============================================================
"""

import re
import json
import logging

logger = logging.getLogger(__name__)

class SystemValidator:
    @staticmethod
    def clean_and_validate_json(raw_text: str) -> str:
        """
        Làm sạch chuỗi phản hồi từ AI, loại bỏ Markdown code block 
        và tự động sửa các lỗi cú pháp JSON phổ biến (thiếu dấu phẩy, dấu phẩy thừa).
        """
        if not raw_text:
            raise ValueError("Chuỗi phản hồi từ AI trống, không thể phân tích JSON.")
        
        text = str(raw_text).strip()
        
        # 1. Cắt bỏ các khối code markdown (ví dụ ```json ... ```) nếu có
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        
        # 2. Trích xuất đoạn JSON chuẩn bắt đầu bằng { hoặc [
        match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
        if match:
            text = match.group(0)
        
        # 3. Thử parse trực tiếp, nếu lỗi thì kích hoạt bộ tự động vá lỗi
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError as initial_err:
            logger.warning(f"Phát hiện lỗi JSON ban đầu, đang tiến hành tự động vá lỗi: {initial_err}")
            repaired_text = SystemValidator._repair_json_string(text)
            try:
                json.loads(repaired_text)
                return repaired_text
            except json.JSONDecodeError as repair_err:
                raise ValueError(
                    f"AI không trả về định dạng JSON hợp lệ sau khi vá lỗi: {str(repair_err)}\n"
                    f"Nội dung gốc từ AI (300 ký tự đầu):\n{raw_text[:300]}..."
                )

    @staticmethod
    def _repair_json_string(json_str: str) -> str:
        """Thuật toán tự động vá các lỗi cú pháp JSON thường gặp ở LLM"""
        # Xóa dấu phẩy thừa trước dấu đóng ngoặc } hoặc ]
        json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        
        # Vá dấu phẩy bị thiếu giữa các dòng kết thúc bằng giá trị và bắt đầu bằng key mới
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
        json_str = re.sub(r'(\d+|true|false|null)\s*\n\s*"', r'\1,\n"', json_str)
        json_str = re.sub(r'([\]\}])\s*\n\s*"', r'\1,\n"', json_str)
        
        return json_str
