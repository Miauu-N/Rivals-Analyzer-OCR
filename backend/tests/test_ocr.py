import os
import json
import pytest
from unittest.mock import patch, MagicMock
from app.services.ocr.history_parser import parse_history

@patch("app.services.ocr.history_parser.model.generate_content")
def test_parse_history_integration(mock_generate_content):
    """Test using a specific static screenshot from the mock folder
    and mocking the Gemini API to avoid real network calls.
    """
    mock_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock"))
    if not os.path.exists(mock_dir):
        pytest.skip(f"Mock directory {mock_dir} does not exist.")

    # Target the specific test screenshot in mock directory
    target_image = "0ddb4b47-3c53-4356-ac14-7920d7a8b26d.png"
    image_path = os.path.join(mock_dir, target_image)
    
    if not os.path.exists(image_path):
        pytest.skip(f"Target test image {target_image} not found in mock folder.")

    # Setup mock response simulating Gemini's JSON output
    mock_response = MagicMock()
    mock_response.text = json.dumps([
        {
            "result": "Victory",
            "kda": "10 / 2 / 5",
            "duration_seconds": 1200,
            "map_name": "Test Map",
            "rank": "GOLD I (+10)",
            "created_at": "2026-06-23T12:00:00"
        }
    ])
    mock_generate_content.return_value = mock_response

    try:
        matches = parse_history(image_path)
    except Exception as e:
        pytest.fail(f"OCR history parser failed to process the image: {e}")

    # Verify our mock worked
    mock_generate_content.assert_called_once()

    assert isinstance(matches, list)
    assert len(matches) == 1
    
    match = matches[0]
    assert match["result"] == "Victory"
    assert match["kda"] == "10 / 2 / 5"
    assert match["duration_seconds"] == 1200
    assert match["map_name"] == "Test Map"
    assert match["rank"] == "GOLD I (+10)"
    assert match["created_at"].isoformat() == "2026-06-23T12:00:00"
