"""
OCR Processing Module - Free Implementation
Supports both digital PDFs (pdfplumber) and scanned PDFs (Tesseract)
"""

import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class OCRProcessor:
    """Handle PDF text extraction using free OCR tools"""

    def __init__(self, ocr_engine='pdfplumber'):
        """
        Initialize OCR processor

        Args:
            ocr_engine: 'pdfplumber' for digital PDFs, 'tesseract' for scanned PDFs
        """
        self.ocr_engine = ocr_engine

    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF using specified OCR engine

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if self.ocr_engine == 'pdfplumber':
            return self._extract_with_pdfplumber(pdf_path)
        elif self.ocr_engine == 'tesseract':
            return self._extract_with_tesseract(pdf_path)
        else:
            # Auto-detect: try pdfplumber first, fall back to tesseract
            try:
                text = self._extract_with_pdfplumber(pdf_path)
                if len(text.strip()) > 50:  # If we got meaningful text
                    return text
                else:
                    print("pdfplumber returned minimal text, trying Tesseract...")
                    return self._extract_with_tesseract(pdf_path)
            except Exception as e:
                print(f"pdfplumber failed: {e}, trying Tesseract...")
                return self._extract_with_tesseract(pdf_path)

    def _extract_with_pdfplumber(self, pdf_path):
        """
        Extract text using pdfplumber (best for digital PDFs with selectable text)

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text
        """
        print(f"Extracting text with pdfplumber from: {pdf_path}")
        text = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text.append(f"\n--- Page {page_num} ---\n")
                        text.append(page_text)

            full_text = ''.join(text)
            print(f"Extracted {len(full_text)} characters using pdfplumber")
            return full_text

        except Exception as e:
            raise Exception(f"pdfplumber extraction failed: {str(e)}")

    def _extract_with_tesseract(self, pdf_path):
        """
        Extract text using Tesseract OCR (best for scanned/image PDFs)

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text
        """
        print(f"Extracting text with Tesseract OCR from: {pdf_path}")
        text = []

        try:
            # Convert PDF pages to images
            print("Converting PDF to images...")
            images = convert_from_path(pdf_path, dpi=300)
            print(f"Converted {len(images)} pages to images")

            # OCR each page
            for page_num, image in enumerate(images, 1):
                print(f"OCR processing page {page_num}/{len(images)}...")
                page_text = pytesseract.image_to_string(image)
                text.append(f"\n--- Page {page_num} ---\n")
                text.append(page_text)

            full_text = ''.join(text)
            print(f"Extracted {len(full_text)} characters using Tesseract")
            return full_text

        except Exception as e:
            raise Exception(f"Tesseract extraction failed: {str(e)}. "
                          f"Make sure Tesseract is installed: 'brew install tesseract' (macOS) "
                          f"or 'apt-get install tesseract-ocr' (Linux)")

    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image using Tesseract

        Args:
            image_path: Path to image file

        Returns:
            str: Extracted text
        """
        print(f"Extracting text from image: {image_path}")

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            print(f"Extracted {len(text)} characters from image")
            return text
        except Exception as e:
            raise Exception(f"Image OCR failed: {str(e)}")


# Test function
def test_ocr(pdf_path):
    """Test OCR on a PDF file"""
    processor = OCRProcessor(ocr_engine='auto')
    text = processor.extract_text_from_pdf(pdf_path)
    print("\n" + "="*50)
    print("EXTRACTED TEXT:")
    print("="*50)
    print(text[:1000])  # Print first 1000 characters
    print("\n" + "="*50)
    print(f"Total length: {len(text)} characters")
    return text


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        test_ocr(sys.argv[1])
    else:
        print("Usage: python ocr_processor.py <path_to_pdf>")
