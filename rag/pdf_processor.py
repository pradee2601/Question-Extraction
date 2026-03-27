import fitz  # PyMuPDF
from PIL import Image
import io
from rag.ocr import extract_text_from_image, clean_text
from utils.logger import setup_logger

logger = setup_logger(__name__)

def process_pdf(file_stream):
    """
    Process a PDF file stream and return extracted text.
    Handles both normal text PDFs and scanned documents (via OCR).
    """
    extracted_text = ""
    try:
        # Open PDF from stream
        pdf_document = fitz.open(stream=file_stream.read(), filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text").strip()
            
            # If page contains substantial text, use it
            if len(text) > 100:
                extracted_text += text + "\n\n"
            else:
                # Page is mostly empty or scanned: fallback to OCR
                logger.info(f"Page {page_num+1} seems to be a scanned image. Running OCR...")
                pix = page.get_pixmap(dpi=300) # High DPI for better OCR
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                ocr_text = extract_text_from_image(pil_image)
                ocr_text = clean_text(ocr_text)
                
                if ocr_text:
                    extracted_text += ocr_text + "\n\n"
                    
        pdf_document.close()
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"Failed to process PDF: {e}")
        return ""

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Simple sliding window text chunker.
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks
