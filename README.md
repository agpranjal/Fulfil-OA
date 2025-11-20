# Fulfil.io - Product Importer

## Running with Docker Compose
1) Copy env template: `cp .env.example .env`
2) Build and start services (API, Celery worker, Redis, Postgres):
   ```bash
   docker-compose up --build
   ```
3) Access the app at `http://localhost:8000` (redirects to the upload page).
4) Static HTML templates are at `/templates/*.html` (upload, products, webhooks, admin).

Compose wiring:
- API: uvicorn on port 8000.
- Worker: Celery worker using Redis broker/result.
- DB: Postgres (`db` service) with default credentials from `.env.example`.
- Redis: `redis` service.