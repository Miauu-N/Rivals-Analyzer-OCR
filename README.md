# Rivals Replay Analyzer

Aplicación web fullstack para subir capturas de pantalla de **Marvel Rivals** y analizarlas con OCR para clasificar el historial de partidas y los scoreboards, ofreciendo un sistema de recomendación de qué partidas volver a visualizar.

## Stack Tecnológico

- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui.
- **Backend:** Python, FastAPI, SQLAlchemy.
- **OCR:** OpenCV, Tesseract OCR.
- **Base de Datos:** PostgreSQL (o SQLite local).
- **Despliegue:** Docker, Docker Compose.

## Requisitos Previos

- Docker y Docker Compose
- (Opcional, para desarrollo local sin Docker) Python 3.10+, Node.js 18+, Tesseract OCR instalado en el sistema.

## Configuración y Ejecución con Docker (Recomendado)

1. Clona el repositorio.
2. Copia `.env.example` a `.env` (si es necesario modificar credenciales).
3. Levanta todos los servicios:
   ```bash
   docker-compose up --build
   ```
4. Accede a las aplicaciones:
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`

## Ejecución Local (Sin Docker)

### Backend
1. Entra a `backend/`: `cd backend`
2. Crea el entorno virtual: `python -m venv venv`
3. Activa el entorno: `source venv/bin/activate` (o `venv\Scripts\activate` en Windows)
4. Instala dependencias: `pip install -r requirements.txt`
5. Ejecuta: `uvicorn app.main:app --reload`
*Nota: Localmente, sin setear `DATABASE_URL`, el backend usará `sqlite:///./sql_app.db` por defecto.*

### Frontend
1. Entra a `frontend/`: `cd frontend`
2. Instala dependencias: `npm install`
3. Ejecuta: `npm run dev`

## Base de Datos
Las migraciones o creación de tablas se hacen automáticamente al iniciar la aplicación Backend (FastAPI).

## Estructura
- `/backend`: API en Python usando FastAPI.
- `/frontend`: App web en Next.js.
