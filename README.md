# DocuFlow – Document Indexing Backend

DocuFlow is a production-ready backend service built with **FastAPI**, **PostgreSQL**, and **Celery**.  
It provides **user authentication**, **document upload**, **asynchronous indexing**, and **admin-level analytics**, all containerized and orchestrated via **Docker Compose**.

## 🚀 Features
- **JWT authentication**
  - User registration & login  
  - Automatic creation of the first admin  
  - Role-based API access (ADMIN / USER)

- **Document lifecycle**
  - Upload real files (PDF, images, docs…)  
  - Metadata stored in PostgreSQL  
  - File storage on disk  
  - Filter/search by status, filename, tags

- **Asynchronous processing**
  - Celery worker processes uploaded files  
  - Simulated indexing → stores indexed text  
  - Scheduled retry (Celery Beat) for FAILED documents

- **Admin tools**
  - Global stats: users, documents, indexed, failed  
  - View all users and documents  
  - Manually retry all FAILED documents

## 🧱 Tech stack
- **FastAPI**  
- **PostgreSQL 16**  
- **SQLAlchemy 2.0**  
- **Alembic migrations**  
- **Celery + Redis**  
- **JWT security using python-jose & passlib**  
- **Pydantic 2.x with rust-compiled core**

## ⚙️ Getting started

### Prerequisites
1. Python **3.11**
2. Rust/Cargo (required by pydantic-core)
3. Docker + Docker Compose (recommended)

### Local setup
```
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs`.

### Run Celery manually
```
celery -A app.core.celery_app.celery_app worker -Q documents -l info
celery -A app.core.celery_app.celery_app beat -l info
```

## 🐳 Docker Compose
To start the full stack:

```
docker compose up --build
```

This launches:
- PostgreSQL  
- Redis  
- API service  
- Celery worker  
- Celery beat scheduler  

## 🧪 Running tests
Inside Docker:

```
docker compose run --rm api pytest
```

## ⚙️ Environment configuration

| Variable | Purpose |
|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Secret for JWT signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration |
| `FILES_DIR` | Upload location |
| `CELERY_BROKER_URL` | Redis broker |
| `CELERY_RESULT_BACKEND` | Redis results |

## 📡 API overview

### Authentication
- `POST /auth/register`
- `POST /auth/token`

### Documents
- `POST /documents/upload`
- `GET /documents`
- `POST /documents/{id}/index`

### Admin
- `GET /admin/stats`
- `POST /admin/documents/retry-failed`

## 📁 Project layout
```
app/
 ├── api/
 ├── core/
 ├── db/
 ├── models/
 ├── schemas/
 ├── tasks/
 └── files/
```

## 📌 Notes
This project simulates document indexing for portfolio/demo purposes and can be extended into:
- Full text search engines (Elasticsearch, Meilisearch)
- Microservices architecture
- Kubernetes deployment

