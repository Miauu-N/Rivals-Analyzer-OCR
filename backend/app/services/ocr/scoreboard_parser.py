import google.generativeai as genai
import json
import re
from PIL import Image
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

def parse_scoreboard(image_path: str) -> dict:
    try:
        img = Image.open(image_path)
        
        prompt = """
        Analiza esta captura de pantalla de un Scoreboard (tabla de puntuaciones) del juego Marvel Rivals.
        El jugador principal ("main user") tiene su nombre escrito en color Naranja o Amarillo (en este caso suele decir MVP, SVP o simplemente está resaltado).
        Extrae la información de la partida y el rendimiento de LOS 12 JUGADORES en un JSON estricto.
        No incluyas markdown, bloques de código (como ```json) ni texto extra, solo el JSON puro.
        
        Estructura exacta:
        {
            "match_info": {
                "result": "Win" o "Loss" o "Draw" (Suele decir VICTORY o DEFEAT arriba a la izquierda),
                "map_name": "Nombre del mapa (está arriba a la derecha en texto pequeño, ej: INTERGALACTIC EMPIRE OF WAKANDA - BIRNIN T'CHALLA)",
                "duration_seconds": Duración total en segundos (convierte el tiempo mm:ss de arriba a la derecha a segundos enteros)
            },
            "performances": [
                {
                    "player_name": "nombre del jugador",
                    "hero_name": "Nombre del personaje de Marvel (dedúcelo viendo su retrato a la izquierda del nombre)",
                    "kills": número bajo el icono de las dos espadas cruzadas (Final Hits),
                    "deaths": número bajo el icono del corazón roto,
                    "assists": número bajo el icono de la espada con la flecha,
                    "damage": número en la columna Damage,
                    "damage_blocked": número en la columna Damage Blocked (mitigación),
                    "healing": número en la columna Healing,
                    "is_main_user": true si su nombre está en color naranja/amarillo, false si está en negro/blanco
                }
            ]
        }
        Asegúrate de extraer las 12 filas de jugadores de la tabla.
        """
        
        response = model.generate_content([prompt, img])
        
        json_str = response.text
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].strip()
            
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"Error parsing scoreboard with Gemini: {e}")
        return None
