# Tasks

## 1. Project Setup
- [x] 1.1 Scaffold FastAPI project structure matching `product-importer/` layout with `app`, `static`, `templates`, and config files.
- [x] 1.2 Configure environment loading (`.env.example`) and settings in `app/config.py` for DB URL, Celery broker/backend, file storage paths, and webhook timeout defaults.
- [x] 1.3 Initialize FastAPI app factory in `app/main.py` wiring routers, static files, templates, and dependency injection.

## 2. Database
- [x] 2.1 Set up SQLAlchemy engine/session management in `app/database.py` and apply migrations or metadata creation hook.
- [x] 2.2 Define `Product` model in `app/models.py` with lowercase unique `sku`, name, description, price, and `active` default true.
- [x] 2.3 Define `Webhook` model in `app/models.py` with `url`, `event_type`, and `active`.
- [x] 2.4 Create Pydantic schemas in `app/schemas.py` for product read/write, webhook read/write, paginated responses, and upload status payload.

## 3. Background Processing
- [x] 3.1 Configure Celery app in `app/celery_app.py` with broker/backend settings and autodiscover tasks.
- [x] 3.2 Implement CSV import task in `app/tasks/importer.py` to stream/process chunks (10k–50k rows), lowercase SKUs, upsert/overwrite existing products, and update progress tracking.
- [x] 3.3 Implement progress tracking utility in `app/services/progress.py` to store/read task state (`status`, counts, percent, message, errors).

## 4. CSV Upload Feature
- [x] 4.1 Implement `POST /upload` in `app/routers/upload.py` to accept CSV upload (max 500k rows), persist temp file, enqueue Celery import task, and return `task_id`.
- [x] 4.2 Implement `GET /upload/status/{task_id}` in `app/routers/upload.py` to return progress payload with status, processed, total, percent, and message.
- [x] 4.3 Add CSV parsing helper in `app/utils/csv_parser.py` to validate rows and stream to importer in chunks with basic validation errors surfaced.

## 5. Product Management API
- [x] 5.1 Implement `GET /products` in `app/routers/products.py` with filters (`sku`, `name`, `active`, `description`) and pagination (`page`, `limit`), returning paginated list.
- [x] 5.2 Implement `POST /products` to create product via service layer, enforcing lowercase unique `sku`.
- [x] 5.3 Implement `PUT /products/{id}` to update product fields, keeping SKU case-insensitive uniqueness.
- [x] 5.4 Implement `DELETE /products/{id}` to delete a single product with graceful handling of missing IDs.

## 6. Bulk Delete
- [x] 6.1 Implement `DELETE /products` in `app/routers/admin.py` to remove all product records with confirmation guard (e.g., query param or header).

## 7. Webhook Management API
- [x] 7.1 Implement `GET /webhooks` in `app/routers/webhooks.py` to list all webhooks.
- [x] 7.2 Implement `POST /webhooks` to create webhook with URL validation and event type.
- [x] 7.3 Implement `PUT /webhooks/{id}` to update webhook fields and active status.
- [x] 7.4 Implement `DELETE /webhooks/{id}` to delete webhook.
- [x] 7.5 Implement `POST /webhooks/test/{id}` to trigger webhook test using `app/tasks/webhook_sender.py`, returning response code/time/error.

## 8. Services and Utilities
- [x] 8.1 Build `product_service.py` for CRUD, pagination, filtering, and SKU normalization logic.
- [x] 8.2 Build `webhook_service.py` for CRUD, enable/disable toggling, and test dispatch helper.
- [x] 8.3 Add generic helpers in `app/utils/helpers.py` for common responses, error handling, and CSV validation utilities.

## 9. Frontend Templates
- [x] 9.1 Create `templates/upload.html` with file input, upload button, progress bar (parsing/validating/importing/percent), and error display; hook to API endpoints via JS.
- [x] 9.2 Create `templates/products.html` with product table, filters, pagination controls, create/edit modal or inline form, and delete action wired to APIs.
- [x] 9.3 Create `templates/admin.html` with “Delete All Products” button and confirmation prompt tied to bulk delete API.
- [x] 9.4 Create `templates/webhooks.html` with list view, add/edit/delete controls, enable/disable toggle, “Test Webhook” button, and display of response code/time/error.

## 10. Frontend Assets
- [x] 10.1 Implement `static/script.js` to handle form submissions, poll upload status, render progress, and manage CRUD UX for products and webhooks.
- [x] 10.2 Implement `static/styles.css` for consistent layout, tables, modals, buttons, progress bars, and state feedback.

## 11. Testing and Validation Hooks
- [ ] 11.1 Add input validation for CSV size (<=500,000 rows) and server-side error messaging for invalid rows.
- [ ] 11.2 Add error handling and response models for all endpoints to align with PRD JSON formats.
