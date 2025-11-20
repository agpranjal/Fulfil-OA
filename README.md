# Fulfil.io - Product Importer

Ingestion and management service for product data with CSV uploads, product CRUD, webhooks, and bulk operations. Built with FastAPI, Celery, Postgres, and Redis; includes simple HTML frontends for manual use.

## API Overview
- `POST /upload`: upload a CSV (up to 500k rows) and enqueue background import. Returns `task_id`.
- `GET /upload/status/{task_id}`: poll progress (`status`, `processed`, `total`, `percent`, `message`).
- `GET /products`: list products with filters (`sku`, `name`, `active`, `description`) and `page`/`limit` pagination.
- `POST /products`: create a product (SKU normalized to lowercase).
- `PUT /products/{id}`: update a product.
- `DELETE /products/{id}`: delete a product.
- `DELETE /products` (admin): bulk delete all products (requires `confirm=true`).
- `GET /webhooks`: list webhooks.
- `POST /webhooks`: create webhook (`url`, `event_type`, `active`).
- `PUT /webhooks/{id}`: update webhook.
- `DELETE /webhooks/{id}`: delete webhook.
- `POST /webhooks/test/{id}`: enqueue a test webhook call and return the Celery task id.

## Project Structure
```
product-importer/
├── app/
│   ├── main.py                # FastAPI app factory + static mounts
│   ├── config.py              # Env-driven settings
│   ├── database.py            # SQLAlchemy engine/session + init_db
│   ├── models.py              # Product, Webhook ORM models
│   ├── schemas.py             # Pydantic schemas
│   ├── routers/               # API routers (upload, products, webhooks, admin)
│   ├── services/              # Service layers (products, webhooks, progress)
│   ├── tasks/                 # Celery tasks (importer, webhook sender)
│   └── utils/                 # Helpers (CSV parsing, helpers)
├── static/                    # CSS/JS assets for the HTML frontends
├── templates/                 # upload.html, products.html, webhooks.html, admin.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example               # Sample environment variables
```

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
