import os
import json
import google.generativeai as genai
from datetime import datetime
import re
from PIL import Image
from app.core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
# Using gemini-3.1-flash-lite-preview for higher free tier limits (500 RPD)
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

def parse_history(image_path: str):
    try:
        # Load the image using Pillow
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return []

    # Prompt engineered to return a strict JSON array
    prompt = """
    Analiza esta captura de pantalla del historial de partidas de Marvel Rivals.
    Extrae la información de todas las partidas visibles en la lista y devuélvelas en un array JSON estricto.
    REGLA MUY IMPORTANTE: Ignora cualquier partida cuyos datos principales (como KDA, duración o resultado) no se puedan leer claramente porque la tarjeta está físicamente cortada por el borde de la imagen. Si la tarjeta está completa y legible, debes incluirla siempre, sin importar su posición.
    No incluyas markdown, bloques de código (como ```json) ni texto extra, solo el JSON puro.
    
    Cada objeto en el array JSON debe tener esta estructura exacta:
    {
      "result": "Victory", "Defeat" o "Draw" (lee literalmente lo que dice la tarjeta: VICTORY → Victory, DEFEAT → Defeat, DRAW → Draw),
      "kda": "Kills / Deaths / Assists" (ejemplo: "14 / 11 / 24"),
      "duration_seconds": número entero de la duración total en segundos,
      "map_name": "nombre del mapa" (ejemplo: "Central Park", "Midtown"),
      "rank": "rango o elo de la partida si aparece" (ejemplo: "GRANDMASTER II (+23)"),
      "created_at": "YYYY-MM-DDTHH:MM:00" (fecha y hora exacta en formato ISO, usando el año 2026 para fechas abreviadas)
    }
    """
    
    try:
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        # Clean up any markdown formatting just in case Gemini ignored the instructions
        text = re.sub(r'```json', '', text)
        text = re.sub(r'```', '', text)
        text = text.strip()
        
        matches_data = json.loads(text)
        
        # Post-process the JSON list to convert dates
        processed_matches = []
        for m in matches_data:
                raw_result = str(m.get("result", "Unknown")).strip().upper()
                if raw_result in ("VICTORY", "WIN"):
                    result = "Victory"
                elif raw_result in ("DEFEAT", "LOSS"):
                    result = "Defeat"
                elif raw_result == "DRAW":
                    result = "Draw"
                else:
                    result = raw_result.capitalize()
                match_data = {
                    "result": result,
                "kda": str(m.get("kda", "Unknown")),
                "duration_seconds": int(m.get("duration_seconds", 0)),
                "map_name": str(m.get("map_name", "Unknown")),
                "rank": str(m.get("rank", "")),
                "created_at": None
            }
            
            # Parse ISO date string
            date_str = m.get("created_at")
            if date_str:
                try:
                    match_data["created_at"] = datetime.fromisoformat(date_str.replace("Z", ""))
                except Exception as date_e:
                    print(f"Error parsing date {date_str}: {date_e}")
            
            processed_matches.append(match_data)
            
        return processed_matches
        
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        return []
