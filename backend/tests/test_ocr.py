import os
import pytest
from app.services.ocr.history_parser import parse_history
from app.core.config import settings

def test_parse_history_integration():
    """Automated integration test using a specific static screenshot from the mock folder
    and calling the real Gemini API.
    """
    mock_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock"))
    if not os.path.exists(mock_dir):
        pytest.skip(f"Mock directory {mock_dir} does not exist.")

    # Target the specific test screenshot in mock directory
    target_image = "0ddb4b47-3c53-4356-ac14-7920d7a8b26d.png"
    image_path = os.path.join(mock_dir, target_image)
    
    if not os.path.exists(image_path):
        pytest.skip(f"Target test image {target_image} not found in mock folder.")

    if not settings.GEMINI_API_KEY:
        pytest.skip("No GEMINI_API_KEY configured to run integration test with Gemini.")

    try:
        matches = parse_history(image_path)
    except Exception as e:
        pytest.fail(f"OCR history parser failed to process the image: {e}")

    assert isinstance(matches, list)
    # Since we are calling the real Gemini API on a real history screenshot,
    # we should get a non-empty list of parsed match dictionaries.
    assert len(matches) > 0, "No matches were returned by the Gemini OCR parser."
    
    for match in matches:
        assert isinstance(match, dict)
        assert "result" in match
        assert match["result"] in ["Victory", "Defeat", "Unknown"]
        assert "kda" in match
        assert "duration_seconds" in match
        assert isinstance(match["duration_seconds"], int)
        assert "map_name" in match
        assert "rank" in match
        assert "created_at" in match
