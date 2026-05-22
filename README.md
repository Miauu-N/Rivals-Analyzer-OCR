# Rivals Analyzer OCR 🎮📊

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Next.js](https://img.shields.io/badge/Next.js-14.1-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.10-009688)

Una aplicación web full-stack diseñada para analizar capturas de pantalla de **Marvel Rivals** utilizando OCR (Reconocimiento Óptico de Caracteres) e Inteligencia Artificial. La plataforma extrae datos de los scoreboards, clasifica el historial de partidas y proporciona un dashboard interactivo con estadísticas y herramientas para la comunidad.

## 🚀 Características Principales

- **Análisis de Partidas por OCR:** Sube capturas de pantalla de tus partidas y deja que el sistema extraiga los datos relevantes (pytesseract + OpenCV).
- **Análisis Semántico con IA:** Integración con la API de Gemini de Google para un procesamiento avanzado de resultados de partidas.
- **Dashboard Interactivo:** Visualiza tus estadísticas de manera clara y profesional.
- **Historial de Partidas:** Un registro completo de tus enfrentamientos, filtrable y analizado.
- **Creador de Tier Lists Interactivo:** Clasifica a los personajes mediante un sistema *drag-and-drop* y exporta los resultados como imágenes de alta calidad.
- **Diseño UI/UX Premium:** Estética orientada al Gaming (Dark Mode), con tonos oscuros (ej. `bg-black`, `bg-gray-950`), bordes sutiles y acentos de colores vibrantes para una experiencia inmersiva.

## 🛠️ Stack Tecnológico

El proyecto está dividido en microservicios, completamente contenerizado mediante Docker Compose para asegurar un entorno consistente.

### Frontend
- **Framework:** Next.js 14.1 (App Router activado)
- **Lenguaje:** TypeScript, React 18
- **Estilos:** Tailwind CSS (con utilidades como `clsx`, `tailwind-merge`) y `lucide-react` para iconografía.
- **Funcionalidades:** Componentes dinámicos e interactivos, generación de imágenes en el cliente mediante `html-to-image`.

### Backend
- **Framework:** FastAPI (ejecutado con Uvicorn)
- **Lenguaje:** Python 3.10+
- **Base de Datos:** PostgreSQL (y soporte para SQLite) mediante SQLAlchemy y migraciones controladas por Alembic.
- **Procesamiento de Datos:** `pytesseract` y `opencv-python-headless` para la extracción de texto, `google-generativeai` para interpretación semántica.
- **Seguridad y Autenticación:** JWT (`python-jose`), encriptación robusta de contraseñas con `bcrypt`.

## 🐳 Arquitectura Docker & Despliegue

La aplicación se ejecuta a través de tres contenedores principales:
- `rivals_backend` (Basado en `python:3.10-slim`)
- `rivals_frontend` (Basado en `node:18-alpine`)
- `rivals_db` (Basado en `postgres:15-alpine`)

> **⚠️ REGLA CRÍTICA SOBRE DEPENDENCIAS**
> El archivo `docker-compose.yml` mapea el código fuente hacia el interior de los contenedores para facilitar el desarrollo en tiempo real, pero los directorios de dependencias (como `node_modules`) se manejan en volúmenes anónimos.
> **NUNCA** corras `npm install` o `pip install` en tu entorno local esperando que la aplicación en ejecución lo detecte. 
> Si modificas el `package.json` o `requirements.txt`, **DEBES reconstruir el contenedor correspondiente**.

## 🔐 Configuración de Entorno

Antes de desplegar en producción o desarrollo, asegúrate de configurar tu archivo `.env` en el directorio del backend. El sistema requiere:
- `SECRET_KEY`: Una cadena segura para firmar los tokens JWT. (Obligatorio, la app fallará sin esto para evitar secretos inseguros).
- `FRONTEND_URL`: La URL de tu frontend (ej. `http://localhost:3000` o tu dominio en Vercel) para configurar estrictamente las políticas de CORS.
- `GEMINI_API_KEY`: Tu clave de Google Generative AI para el procesamiento semántico.

## ⚙️ Comandos Frecuentes

Asegúrate de tener Docker y Docker Compose instalados.

**1. Levantar el proyecto completo:**
```bash
docker compose up -d
```

**2. Ver logs de los servicios en tiempo real:**
```bash
docker compose logs -f frontend
# o
docker compose logs -f backend
```

**3. Reconstruir tras instalar nuevas dependencias:**
- Si agregas una librería al **Frontend**:
  ```bash
  docker compose up -d --build frontend
  ```
- Si agregas una librería al **Backend**:
  ```bash
  docker compose up -d --build backend
  ```

---
*Este proyecto está diseñado para mi portfolio personal, destacando habilidades en desarrollo Full-Stack moderno, integración de Inteligencia Artificial (LLMs), visión computacional (OCR), y prácticas sólidas de despliegue mediante Docker.*
