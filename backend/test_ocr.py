import os
import json
from app.services.ocr.history_parser import parse_history

uploads_dir = "uploads"
for f in os.listdir(uploads_dir):
    if f.endswith(".png"):
        path = os.path.join(uploads_dir, f)
        print(f"--- Processing {f} with Gemini ---")
        
        try:
            matches = parse_history(path)
            for m in matches:
                print(m)
        except Exception as e:
            print("Error parsing:", e)
        print("\n")
        break # Just test the first one
