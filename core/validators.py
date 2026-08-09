import json

class SystemValidator:
    """
    Lớp kiểm tra tính toàn vẹn cấp hệ thống.
    Xử lý làm sạch và xác thực dữ liệu thô từ AI trước khi đưa vào Pydantic.
    """
    
    @staticmethod
    def clean_and_validate_json(raw_text: str) -> str:
        """Làm sạch các thẻ Markdown bao quanh chuỗi JSON (nếu có)."""
        clean_text = raw_text.strip()
        
        # Bóc tách thẻ ```json nếu AI cố tình in ra
        if clean_text.startswith("```json"):
            clean_text = clean_text.replace("```json", "", 1)
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        clean_text = clean_text.strip()
        
        # Thử parse nhanh để đảm bảo đây là JSON hợp lệ
        try:
            json.loads(clean_text)
            return clean_text
        except json.JSONDecodeError as e:
            raise ValueError(f"Hệ thống từ chối đầu vào. AI không trả về định dạng JSON hợp lệ: {str(e)}\n\nNội dung lỗi: {clean_text[:200]}...")
