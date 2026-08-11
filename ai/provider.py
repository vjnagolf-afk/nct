# -*- coding: utf-8 -*-
"""
============================================================
MODULE: ai/provider.py
Nhiệm vụ: Lớp cơ sở (Base Class - Interface) định nghĩa giao diện chung 
cho tất cả các bộ cung cấp AI (OpenAI, Gemini,...).
============================================================
"""

from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        """
        Gửi yêu cầu tới AI và bắt buộc trả về một chuỗi định dạng JSON hợp lệ.
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """
        Gửi yêu cầu tới AI và trả về chuỗi văn bản thông thường.
        """
        pass
