import pytesseract
from PIL import Image
import io
from config import Config
from utils.logger import setup_logger
import os

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD_PATH

logger = setup_logger(__name__)

def extract_text_from_image(image):
    """
    Extract text from a PIL Image object using Pytesseract.
    """
    try:
        # Check if tesseract cmd exists
        if not os.path.exists(Config.TESSERACT_CMD_PATH):
            logger.warning(f"Tesseract not found at {Config.TESSERACT_CMD_PATH}. OCR will fail.")
        
        # If image is bytes, convert to PIL Image
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""

def clean_text(text):
    """
    Basic text cleaning.
    """
    if not text:
        return ""
    # Remove excessive newlines
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return text
