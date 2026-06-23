import pytest
from fastapi import status
from app.models.match import Match
from app.models.performance import Performance
from app.models.user import User

@pytest.fixture
def test_user_and_token(client, db_session):
    # Creamos un usuario específicamente para estos tests
    email = "analytics@example.com"
    password = "password123"
    client.post("/api/auth/register", json={"email": email, "password": password})
    
    # Hacemos login para obtener el token
    login_response = client.post("/api/auth/login", data={"username": email, "password": password})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Obtenemos el usuario de la DB para poder asignarle las partidas
    user = db_session.query(User).filter(User.email == email).first()
    return user, headers


def test_analytics_summary_empty(client, test_user_and_token):
    _, headers = test_user_and_token
    
    # Si no hay partidas, el sistema debería manejarlo sin crashear y devolver 0s
    response = client.get("/api/analytics/summary", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_matches"] == 0
    assert data["win_rate"] == "0%"
    assert data["avg_kda"] == "0.0"
    assert data["top_roles"] == []


def test_analytics_summary_with_data(client, db_session, test_user_and_token):
    user, headers = test_user_and_token
    
    # 1. Insertamos 3 Partidas (2 Victorias, 1 Derrota)
    m1 = Match(user_id=user.id, result="Victory", map_name="Central Park", duration_seconds=600)
    m2 = Match(user_id=user.id, result="Victory", map_name="Midtown", duration_seconds=700)
    m3 = Match(user_id=user.id, result="Defeat", map_name="Central Park", duration_seconds=500)
    
    db_session.add_all([m1, m2, m3])
    db_session.commit()
    
    # 2. Insertamos la "Performance" de nuestro usuario en esas partidas
    # Match 1: Duelist (10 kills, 2 deaths, 5 assists)
    p1 = Performance(match_id=m1.id, is_main_user=True, kills=10, deaths=2, assists=5, role="Duelist")
    # Match 2: Duelist (5 kills, 1 deaths, 10 assists)
    p2 = Performance(match_id=m2.id, is_main_user=True, kills=5, deaths=1, assists=10, role="Duelist")
    # Match 3: Vanguard (2 kills, 5 deaths, 2 assists)
    p3 = Performance(match_id=m3.id, is_main_user=True, kills=2, deaths=5, assists=2, role="Vanguard")
    
    db_session.add_all([p1, p2, p3])
    db_session.commit()
    
    # 3. Le pegamos al endpoint de analytics
    response = client.get("/api/analytics/summary", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    
    # 4. Verificamos que la lógica de negocio calcule todo PERFECTO
    assert data["total_matches"] == 3
    
    # Win rate: 2 victorias de 3 partidas = 66.666...% -> El endpoint lo formatea a 1 decimal ("66.7%")
    assert data["win_rate"] == "66.7%"
    
    # KDA Total: 
    # Totales: Kills = 17, Deaths = 8, Assists = 17
    # KDA Formula: (Kills + Assists) / Deaths -> (17 + 17) / 8 = 34 / 8 = 4.25
    assert data["avg_kda"] == "4.25"
    
    # Top roles: Jugó 2 veces con Duelist y 1 con Vanguard
    assert data["top_roles"] == ["Duelist", "Vanguard"]
