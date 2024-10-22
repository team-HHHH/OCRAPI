from .easy_ocr import job_easy_ocr, job_easy_ocr_boxes
from .tesseract.job import job_tesseract, job_tesseract_boxes
from .easy_paddle_ocr import job_paddle_ocr

__all__ = [
    "job_easy_ocr",
    "job_easy_ocr_boxes",
    "job_tesseract",
    "job_tesseract_boxes",
    "job_paddle_ocr"
]
