"""Optional EasyOCR adapter, invoked only for confirmed events."""
from __future__ import annotations
class OcrEngine:
    def __init__(self):
        try:
            import easyocr; self.reader=easyocr.Reader(["en"],gpu=False)
        except Exception: self.reader=None
    def read(self,image): return self.reader.readtext(image) if self.reader is not None else []
