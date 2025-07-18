# NOTE: This script is experimental and pending Paperless-ngx integration.
# It is not currently used in production. See documentation for details.
import os
import cv2
import pytesseract
from pdf2image import convert_from_path
from typing import List, Dict, Optional
import tempfile
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ForceScanResult:
    def __init__(self, text: str, confidence: float, pages: int, error: Optional[str] = None):
        self.text = text
        self.confidence = confidence
        self.pages = pages
        self.error = error

class ForceScanner:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def scan_file(self, file_path: str) -> ForceScanResult:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self._scan_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self._scan_image(file_path)
        else:
            return ForceScanResult('', 0.0, 0, error='Unsupported file type')

    def _scan_pdf(self, pdf_path: str) -> ForceScanResult:
        try:
            # Try to extract images from PDF
            with tempfile.TemporaryDirectory() as tmpdir:
                images = convert_from_path(pdf_path, output_folder=tmpdir, fmt='png')
                if not images:
                    return ForceScanResult('', 0.0, 0, error='No images extracted from PDF')
                texts = []
                confidences = []
                for img in images:
                    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    proc_img = self._preprocess_image(img_cv)
                    text, conf = self._ocr_image(proc_img)
                    texts.append(text)
                    confidences.append(conf)
                full_text = '\n'.join(texts)
                avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                return ForceScanResult(full_text, avg_conf, len(images))
        except Exception as e:
            logger.error(f'PDF force scan failed: {e}')
            return ForceScanResult('', 0.0, 0, error=str(e))

    def _scan_image(self, img_path: str) -> ForceScanResult:
        try:
            img = cv2.imread(img_path)
            if img is None:
                return ForceScanResult('', 0.0, 0, error='Image could not be read')
            proc_img = self._preprocess_image(img)
            text, conf = self._ocr_image(proc_img)
            return ForceScanResult(text, conf, 1)
        except Exception as e:
            logger.error(f'Image force scan failed: {e}')
            return ForceScanResult('', 0.0, 0, error=str(e))

    def _preprocess_image(self, img):
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Binarize
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, h=30)
        # (Optional) Deskew, more advanced preprocessing can be added here
        return denoised

    def _ocr_image(self, img):
        # Run Tesseract OCR
        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=custom_config)
        text = ' '.join(data['text'])
        # Calculate average confidence
        confs = [float(c) for c in data['conf'] if c.isdigit()]
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return text, avg_conf

# Example usage:
# scanner = ForceScanner()
# result = scanner.scan_file('/path/to/failed.pdf')
# print(result.text, result.confidence, result.pages, result.error) 