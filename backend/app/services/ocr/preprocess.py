import cv2
import numpy as np

def preprocess_for_ocr(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Scale up the image to improve OCR accuracy for small text
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Apply bilateral filter to remove noise while keeping edges sharp
    blur = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Adaptive thresholding to handle uneven lighting (common in game UIs)
    # The game UI has dark background with white text, or yellow background with black text.
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Invert the image! Tesseract is heavily optimized for BLACK text on WHITE background.
    # Since game text is usually white on dark, the threshold makes it white on black.
    # Inverting it will make it black on white.
    thresh = cv2.bitwise_not(thresh)

    return image, gray, thresh
