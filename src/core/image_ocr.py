import base64
import io
import logging
import os
from typing import List

from PIL import Image, UnidentifiedImageError
import pytesseract

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ImageOCR:
    """
    Extract text from a list of base64‐encoded documents.
    Only tries to OCR if the data URI mime type starts with 'image/'.
    """

    def __init__(self):
        # Allow override of the tesseract command
        self.tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        logger.info(f"Using TESSERACT_CMD='{self.tesseract_cmd}'")

    def extract_texts(self, documents: List[str]) -> List[str]:
        texts: List[str] = []
        for idx, data_uri in enumerate(documents):
            # split out "data:<mime>;base64,<b64>"
            try:
                header, b64data = data_uri.split(",", 1)
            except ValueError:
                logger.warning(f"Document #{idx}: malformed data URI, skipping")
                continue

            mime = header.split(";")[0].removeprefix("data:")
            if not mime.startswith("image/"):
                logger.warning(f"Document #{idx}: mime='{mime}' is not an image, skipping OCR")
                continue

            try:
                img_bytes = io.BytesIO(base64.b64decode(b64data))
                with Image.open(img_bytes) as img:
                    text = pytesseract.image_to_string(img)
                texts.append(text)
                logger.info(f"Document #{idx}: OCR succeeded, {len(text)} chars")
            except UnidentifiedImageError:
                logger.warning(f"Document #{idx}: not a valid image file, skipping")
            except Exception as e:
                logger.exception(f"Document #{idx}: unexpected OCR error, skipping")
        return texts