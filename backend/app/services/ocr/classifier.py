import pytesseract
import cv2
from .preprocess import preprocess_for_ocr

def classify_image(image_path: str) -> str:
    image, gray, thresh = preprocess_for_ocr(image_path)
    
    h, w = thresh.shape
    top_crop = thresh[0:int(h*0.2), 0:w]
    
    text = pytesseract.image_to_string(top_crop, config='--psm 11').upper()
    
    # "HISTORY" is often lost due to yellow on yellow background, but "CAREER" is clearly visible in the top left.
    if "CAREER" in text or "HISTORY" in text or "MODES" in text:
        return "history"
    elif "SCOREBOARD" in text or "STATISTICS" in text or "PERFORMANCE" in text:
        return "scoreboard"
        
    # Default to history as best effort if we can't classify
    return "history"
