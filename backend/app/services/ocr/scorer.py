def get_rank_score(rank_str: str) -> int:
    if not rank_str:
        return 0
        
    rank_str = rank_str.upper()
    
    if "ONE ABOVE ALL" in rank_str or "ONEABOVEALL" in rank_str:
        return 11
    if "ETERNITY" in rank_str:
        return 10
        
    # Determinar division (el OCR puede leer I! o Ill)
    division = 0
    if " III" in rank_str or " ILL" in rank_str or " 3" in rank_str:
        division = 3
    elif " II" in rank_str or " I!" in rank_str or " 2" in rank_str:
        division = 2
    elif " I" in rank_str or " 1" in rank_str:
        division = 1
        
    # Calcular base según el tier
    if "CELESTIAL" in rank_str:
        base = 6
    elif "GRANDMASTER" in rank_str:
        base = 3
    elif "DIAMOND" in rank_str or "DIAMANTE" in rank_str:
        base = 0
    else:
        # Bronce, Plata, Oro, Platino
        return 0
        
    if division == 0:
        division = 3 # Si el OCR falla en ver el numero, asume la mas baja del tier
        
    # Diamante 3 = 1, Diamante 2 = 2, Diamante 1 = 3
    # Grandmaster 3 = 4 ... Celestial 1 = 9
    return base + (4 - division)

def get_duration_score(seconds: int) -> int:
    if seconds < 600:
        return 0
        
    # Empieza de 10 minutos = 1 punto
    score = 1
    
    # Gana 2 puntos mas por cada 5 minutos que pasen
    extra_5_min_blocks = (seconds - 600) // 300
    if extra_5_min_blocks > 0:
        score += (extra_5_min_blocks * 2)
        
    return score

def calculate_replay_score(match_data: dict) -> float:
    score = 0.0
    
    rank_str = match_data.get('rank', '')
    score += get_rank_score(rank_str)
    
    duration = match_data.get('duration_seconds', 0)
    score += get_duration_score(duration)
    
    return float(score)
