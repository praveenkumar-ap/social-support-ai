"""
DocumentProcessor: handles ingestion and extraction of text from various document types
(e.g., PDFs, images, raw text/base64), returning structured data for downstream processing.
"""

import logging
import base64
import io
from typing import List, Dict

import requests
from PIL import Image
import PyPDF2
import pytesseract  # Ensure pytesseract and Tesseract are installed in your environment

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, ocr_language: str = 'eng'):
        """
        Initialize the document processor.
        
        :param ocr_language: language code for OCR (default 'eng')
        """
        self.ocr_language = ocr_language

    def process(self, documents: List[str], applicant_id: str) -> Dict:
        """
        Process a list of document references (URLs or base64 strings) and extract text.
        
        :param documents: list of document inputs (URLs or base64 data URIs)
        :param applicant_id: identifier for the applicant (for logging context)
        :return: dict containing applicant_id and list of extracted document texts
        """
        processed_data = {
            "applicant_id": applicant_id,
            "documents": []
        }

        for idx, doc_ref in enumerate(documents):
            try:
                logger.info(f"Processing document {idx} for applicant {applicant_id}")
                raw_bytes = self._fetch_bytes(doc_ref)
                text = self._extract_text(raw_bytes)
                processed_data["documents"].append({
                    "document_index": idx,
                    "text": text
                })
                logger.debug(f"Extracted text for document {idx}: {text[:100]}...")
            except Exception:
                logger.exception(f"Failed to process document index {idx} for applicant {applicant_id}")
                # Continue processing remaining docs
        return processed_data

    def _fetch_bytes(self, doc_ref: str) -> bytes:
        """
        Fetch raw bytes from a document reference. Supports HTTP URLs or base64 data URIs.
        
        :param doc_ref: URL string or data URI
        :return: raw bytes of the document
        """
        if doc_ref.startswith(("http://", "https://")):
            response = requests.get(doc_ref, timeout=10)
            response.raise_for_status()
            return response.content

        # Assume base64 data URI: "data:<mime>;base64,<encoded>"
        if doc_ref.startswith("data:") and ";base64," in doc_ref:
            try:
                _, b64data = doc_ref.split(";base64,", 1)
                return base64.b64decode(b64data)
            except Exception:
                logger.error("Invalid base64 document data URI")
                raise

        # Fallback: treat as raw text
        logger.warning("Unrecognized document format, treating input as raw text")
        return doc_ref.encode('utf-8')

    def _extract_text(self, raw_bytes: bytes) -> str:
        """
        Extract text from raw document bytes. Tries PDF parsing first, then OCR on images,
        and falls back to plaintext decoding.
        
        :param raw_bytes: raw bytes of the document
        :return: extracted text
        """
        # Try PDF parsing
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
            text_pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(text_pages).strip()
            if text:
                return text
        except Exception:
            logger.debug("PDF parsing failed, trying image OCR", exc_info=True)

        # Try image OCR
        try:
            image = Image.open(io.BytesIO(raw_bytes))
            text = pytesseract.image_to_string(image, lang=self.ocr_language).strip()
            if text:
                return text
        except Exception:
            logger.debug("Image OCR failed, falling back to raw text", exc_info=True)

        # Fallback to UTF-8 text
        try:
            return raw_bytes.decode('utf-8', errors='ignore')
        except Exception:
            logger.warning("Failed to decode bytes as UTF-8, returning empty string")
            return ""