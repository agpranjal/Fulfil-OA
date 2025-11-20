# Product Requirements Document (PRD)

## 1. Scope
This PRD defines the **features to be built**, including:
- API endpoints  
- Frontend functionality  
- Database structure  
- Project folder structure  

No deployment or testing details are included.

---

## 2. Core Functional Features

## 2.1 CSV Product Upload
### **Frontend Requirements**
- A page with a file upload input (`upload.html`)
- A button to upload CSV files (up to 500,000 rows)
- A progress bar showing:
  - Parsing
  - Validating
  - Importing
  - Percentage completed
- Display error message if upload fails

### **API Endpoints**
#### **POST /upload**
- Accepts CSV file  
- Returns a `task_id` to track background processing

#### **GET /upload/status/{task_id}**
Returns:
```json
{
  "status": "processing | completed | error",
  "processed": 120000,
  "total": 500000,
  "percent": 24.0,
  "message": "Parsing CSV"
}
```

### **Backend Requirements**
- Temporarily save uploaded file  
- Celery task processes CSV in chunks (10k–50k rows)
- SKU handling:
  - Case-insensitive
  - Overwrite if exists

---

## 2.2 Product Management
### **Frontend Requirements**
- `products.html`
- Table listing products with pagination
- Filters:
  - sku  
  - name  
  - active status  
  - description  
- Create/Edit product (modal or inline)
- Delete product with confirmation

### **API Endpoints**
#### **GET /products**
Query params: `?sku=&name=&active=&description=&page=&limit=`

#### **POST /products**
Create product.

#### **PUT /products/{id}**
Update product.

#### **DELETE /products/{id}**
Delete product.

---

## 2.3 Bulk Delete
### **Frontend Requirements**
- `admin.html` with a “Delete All Products” button
- Confirmation prompt

### **API Endpoint**
#### **DELETE /products**
Removes all product records.

---

## 2.4 Webhook Management
### **Frontend Requirements**
- `webhooks.html`
- List all webhooks
- Add/Edit/Delete webhooks
- Enable/disable via toggle
- “Test Webhook” button
- Display:
  - Response code  
  - Response time  
  - Error (if any)

### **API Endpoints**
#### **GET /webhooks**
List all.

#### **POST /webhooks**
Create webhook.

#### **PUT /webhooks/{id}**
Update webhook.

#### **DELETE /webhooks/{id}**
Delete webhook.

#### **POST /webhooks/test/{id}**
Triggers a webhook test.

### **Sample Test Webhook Payload**
```json
{
  "event": "webhook.test",
  "timestamp": "2025-11-19T14:05:12Z",
  "message": "This is a test webhook fired from your product importer app."
}
```

---

# 3. Database Schema

## 3.1 Product Table
| Column       | Type    | Notes                            |
|--------------|---------|----------------------------------|
| id           | int     | Primary key                      |
| sku          | text    | Lowercase, unique                |
| name         | text    |                                  |
| description  | text    |                                  |
| price        | numeric |                                  |
| active       | boolean | Default: true                    |

---

## 3.2 Webhook Table
| Column       | Type    | Notes                    |
|--------------|---------|--------------------------|
| id           | int     | Primary key              |
| url          | text    | Target endpoint          |
| event_type   | text    | e.g. product.imported    |
| active       | boolean | Enable/disable           |

---

# 4. Project Folder Structure

```
product-importer/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── celery_app.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── upload.py
│   │   ├── products.py
│   │   ├── webhooks.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── product_service.py
│   │   ├── webhook_service.py
│   │   └── progress.py
│   │
│   ├── tasks/
│   │   ├── importer.py
│   │   └── webhook_sender.py
│   │
│   └── utils/
│       ├── csv_parser.py
│       └── helpers.py
│
├── static/
│   ├── styles.css
│   └── script.js
│
├── templates/
│   ├── upload.html
│   ├── products.html
│   ├── webhooks.html
│   └── admin.html
│
├── requirements.txt
├── .env.example
└── README.md
```
