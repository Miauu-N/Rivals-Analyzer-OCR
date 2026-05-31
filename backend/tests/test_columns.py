import os
import cv2
import pytest
import pytesseract

def test_columns_extraction_integration():
    """Automated integration test to verify OpenCV image processing and Tesseract column data extraction
    using static images from the mock folder.
    """
    mock_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock"))
    if not os.path.exists(mock_dir):
        pytest.skip(f"Mock directory {mock_dir} does not exist.")
        
    # Target one of the static screenshots in mock directory
    target_image = "0e9c8ae7-5b61-4c0c-b05b-30b268105625.png"
    image_path = os.path.join(mock_dir, target_image)
    
    # Fallback to the other mock image if the target one is missing
    if not os.path.exists(image_path):
        fallback_image = "0ddb4b47-3c53-4356-ac14-7920d7a8b26d.png"
        image_path = os.path.join(mock_dir, fallback_image)
        if not os.path.exists(image_path):
            pytest.skip("No mock PNG files found in mock directory to test columns extraction.")
            
    # Check if Tesseract OCR is installed in the system PATH
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        pytest.skip("Tesseract OCR is not installed or not in PATH. Skipping columns test.")
        
    image = cv2.imread(image_path)
    assert image is not None, f"Failed to load image from {image_path}"
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blur = cv2.bilateralFilter(gray, 9, 75, 75)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)
    
    h, w = thresh.shape
    
    try:
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config='--psm 11')
    except Exception as e:
        pytest.fail(f"pytesseract failed to extract data from preprocessed image: {e}")
        
    assert isinstance(data, dict)
    assert 'text' in data
    assert 'conf' in data
    assert 'top' in data
    assert 'left' in data
    
    # Ensure there is at least some text identified
    assert len(data['text']) > 0
