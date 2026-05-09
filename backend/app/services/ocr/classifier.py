import google.generativeai as genai
from PIL import Image
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

def classify_image(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        
        prompt = """Mira esta captura de pantalla del juego Marvel Rivals.
        Clasifícala en UNA de estas dos categorías y responde SOLO con esa palabra, sin explicación:
        - "scoreboard": Si muestra la pantalla de puntuaciones al final de una partida. Se identifica por tener el texto VICTORY, DEFEAT o DRAW en letras grandes a la izquierda, y una tabla con los 12 jugadores con sus estadísticas (Damage, Healing, Final Hits, etc).
        - "history": Si muestra la pantalla de historial/carrera (Career History). Se identifica por tener una barra de pestañas en la parte superior (con OVERVIEW, STATISTICS, HISTORY, etc) y una lista de partidas pasadas con fechas.
        
        Responde solo con la palabra: scoreboard o history"""
        
        response = _model.generate_content([prompt, img])
        result = response.text.strip().lower()
        
        if "scoreboard" in result:
            return "scoreboard"
        elif "history" in result:
            return "history"
        else:
            return "history"  # safe fallback
            
    except Exception as e:
        print(f"Error classifying image with Gemini: {e}")
        return "history"
