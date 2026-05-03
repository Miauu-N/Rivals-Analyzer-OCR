import os
import cv2
import pytesseract

uploads_dir = "uploads"
# Process first file
for f in os.listdir(uploads_dir):
    if f.endswith(".png"):
        path = os.path.join(uploads_dir, f)
        print(f"--- Processing {f} ---")
        
        image = cv2.imread(path)
        h_orig, w_orig, _ = image.shape
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        blur = cv2.bilateralFilter(gray, 9, 75, 75)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        thresh = cv2.bitwise_not(thresh)
        
        h, w = thresh.shape
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config='--psm 11')
        
        n_boxes = len(data['text'])
        
        # Group by Y tolerance
        rows = {}
        Y_TOLERANCE = 150
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 30:
                text = data['text'][i].strip()
                if not text: continue
                
                y = data['top'][i]
                x = data['left'][i]
                
                matched_row_y = None
                for row_y in rows.keys():
                    if abs(y - row_y) < Y_TOLERANCE:
                        matched_row_y = row_y
                        break
                
                if matched_row_y is None:
                    rows[y] = []
                    matched_row_y = y
                    
                rows[matched_row_y].append({"text": text, "x": x, "y": y})
                
        for y_coord, items in sorted(rows.items()):
            # Sort items by X coordinate
            items.sort(key=lambda item: item['x'])
            
            # Reconstruct string
            full_text = " ".join([item['text'] for item in items])
            if "VICTORY" not in full_text.upper() and "DEFEAT" not in full_text.upper():
                continue
                
            print("\nRow Y:", y_coord)
            
            col_result = []
            col_kda = []
            col_rank = []
            col_date = []
            col_map = []
            
            for item in items:
                rel_x = item['x'] / w
                if rel_x < 0.22:
                    col_result.append(item['text'])
                elif rel_x >= 0.22 and rel_x < 0.38:
                    col_kda.append(item['text'])
                elif rel_x >= 0.38 and rel_x < 0.55:
                    col_rank.append(item['text'])
                elif rel_x >= 0.55 and rel_x < 0.70:
                    col_date.append(item['text'])
                else:
                    col_map.append(item['text'])
                    
            print(f"RESULT: {' '.join(col_result)}")
            print(f"KDA: {' '.join(col_kda)}")
            print(f"RANK: {' '.join(col_rank)}")
            print(f"DATE: {' '.join(col_date)}")
            print(f"MAP: {' '.join(col_map)}")
        break
