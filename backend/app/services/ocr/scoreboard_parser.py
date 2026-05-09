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
        El jugador principal ("main user") tiene su nombre escrito en color Naranja o Amarillo (suele tener el badge de MVP o SVP).
        Extrae la información de la partida y el rendimiento de LOS 12 JUGADORES en un JSON estricto.
        No incluyas markdown, bloques de código (como ```json) ni texto extra, solo el JSON puro.
        
        IMPORTANTE sobre el KDA: En la tabla hay una columna llamada "Final Hits" que NO es el KDA.
        El K/D/A (kills, deaths, assists) son los 3 números pequeños que aparecen DENTRO DE LA MISMA CELDA del nombre del jugador, justo debajo o al lado del nombre, con los iconos de espada cruzada / corazón roto / espada con flecha. Por ejemplo: "10  2  15" significa K=10, D=2, A=15.
        La columna "Final Hits" es una columna separada a la derecha y NO debe usarse para el KDA.
        
        Estructura exacta:
        {
            "match_info": {
                "result": "Victory" o "Defeat" o "Draw" (dice VICTORY, DEFEAT o DRAW arriba a la izquierda),
                "map_name": "Nombre del mapa (arriba a la derecha en texto pequeño)",
                "duration_seconds": duración en segundos (convierte mm:ss a segundos enteros),
                "replay_id": "número de Replay ID en la esquina inferior derecha. Si no se ve, usa null."
            },
            "performances": [
                {
                    "player_name": "nombre del jugador tal cual aparece",
                    "role": "ROL del jugador según el ICONO PEQUEÑO a la izquierda del nombre: Vanguard (escudo), Duelist (espadas cruzadas), Strategist (corazón/cruz médica). Si no puedes determinarlo escribe Unknown.",
                    "kills": el primer número del KDA que aparece EN LA CELDA del nombre del jugador (icono espada cruzada), NO es Final Hits,
                    "deaths": el segundo número del KDA en la celda del jugador (icono corazón roto),
                    "assists": el tercer número del KDA en la celda del jugador (icono espada con flecha),
                    "final_hits": número de la columna "Final Hits" (la primera columna numérica a la derecha),
                    "damage": número en la columna Damage,
                    "damage_blocked": número en la columna Damage Blocked,
                    "healing": número en la columna Healing,
                    "is_main_user": true si el nombre está en naranja/amarillo, false si está en blanco/gris
                }
            ]
        }
        Asegúrate de extraer las 12 filas de jugadores.
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
