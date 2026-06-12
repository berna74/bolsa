# ConTodoGusto - Bolsa Laboral Gastronómica

Aplicación full stack para que trabajadores gastronómicos puedan registrarse, iniciar sesión y publicar su perfil profesional con datos personales, experiencia laboral y referencias.

## Stack
- Frontend: Vue 3 + Vite
- Backend: Django + Django REST Framework + JWT
- Base de datos: PostgreSQL
- Infraestructura: Docker Compose

## Estructura
- `backend/`: API REST y lógica de negocio
- `frontend/`: SPA para candidatos
- `docker-compose.yml`: orquestación de servicios

## Puesta en marcha
1. Abrí la carpeta del proyecto.
2. Ejecutá:
   ```bash
   docker compose up --build
   ```
3. URLs:
   - Frontend: `http://localhost:5174`
   - Backend API: `http://localhost:8001/api`
   - Healthcheck: `http://localhost:8001/api/health/`

## Flujo funcional
1. Crear cuenta en la pantalla de autenticación.
2. Iniciar sesión.
3. Completar perfil profesional.
4. Cargar experiencias laborales.
5. Cargar referencias profesionales.

## Endpoints principales
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `GET/PUT /api/profile/`
- `GET/POST/DELETE /api/experiences/`
- `GET/POST/DELETE /api/references/`

## Nota de diseño
No fue posible consultar automáticamente `contodogusto.com.ar` desde el entorno actual. Se aplicó una estética gastronómica cálida (tonos tierra, acentos anaranjados y tipografía editorial) para mantener una identidad visual coherente con una marca del rubro.
