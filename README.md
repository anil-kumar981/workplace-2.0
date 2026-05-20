# Enterprise CRM Backend

A high-performance, asynchronous REST API service built with **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, and **Pydantic v2**. This application serves as the robust backend directory for user management, role-based access control (RBAC), and enterprise ledger management.

---

## 🛠️ Tech Stack
* **Framework**: FastAPI (Asynchronous Python Web Framework)
* **ORM**: SQLAlchemy 2.0 (using asynchronous engine)
* **Database Driver**: `asyncpg` (PostgreSQL async client)
* **Database Migrations**: Alembic (using `async` template)
* **Settings & Validation**: Pydantic v2 & `python-dotenv`
* **Development Server**: Uvicorn

---

## 🚀 Step-by-Step Setup Guide

Follow these instructions to clone, install, configure, and run the backend service on your local machine.

### 1. Clone the Project
Open your terminal, navigate to your desired directory, and clone the repository:
```bash
git clone <repository_url>
cd workplace
```

### 2. Set Up the Virtual Environment
Create a Python virtual environment to keep dependencies isolated:

* **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
With the virtual environment activated, install all required packages:
```bash
pip install -r req.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory of the project and populate it with your environment configuration. For example:

```env
PORT=8000
IP_ADDRESS=127.0.0.1
DATABASE_URL="postgresql+asyncpg://postgres:your_password@localhost:5432/anil_db"
JWT_SECRET_KEY="your_jwt_secret_key"
JWT_ALGORITHM="HS256"
JWT_EXPIRES_IN="1h"
SALT_ROUNDS=12
JWT_COOKIE_NAME="access_token"

MAIL_HOST="smtp.gmail.com"
MAIL_PORT=587
MAIL_USER="your_email@gmail.com"
MAIL_PASSWORD="your_smtp_app_password"
MAIL_SECURE=false
MAIL_FROM="your_email@gmail.com"

APP_TITLE="Enterprise CRM Backend"
APP_DESCRIPTION="High-performance, asynchronous REST API services built with FastAPI, SQLAlchemy 2.0, and Pydantic v2."
APP_VERSION="1.0.0"
```

> [!NOTE]
> Make sure to replace `your_password`, `your_jwt_secret_key`, and mail credentials with your actual database credentials and secrets.

---

## 💾 Database Setup & Migrations

### Option A: Reset and Seed the Database (Recommended for Fresh Dev Setup)
If you want to clear all existing data, recreate all tables from scratch, and seed roles, permissions, and an admin user:
```bash
python -m app.database.seed
```

> [!CAUTION]
> This command runs a drop-and-create sequence (`drop_all` followed by `create_all`). Do not run this command in a production environment as it will clear all database tables!

---

### Option B: Run Migrations with Alembic (Incremental Structural Updates)
To apply the version-controlled migrations incrementally without losing existing data, run:
```bash
alembic upgrade head
```

#### Creating a New Migration
Whenever you modify your database models (under `app/models/`), you can autogenerate a new Alembic migration:
1. Ensure your model is imported in `app/models/__init__.py`.
2. Generate the migration script:
   ```bash
   alembic revision --autogenerate -m "Describe your schema changes"
   ```
3. Apply the generated migration script to your database:
   ```bash
   alembic upgrade head
   ```

---

## 🏃 Run the Application

Start the development server using Uvicorn:

```bash
python main.py
```

Alternatively, you can run it via the Uvicorn CLI directly:
```bash
uvicorn main:app --reload --port 8000
```

Once the server is running, you can access the interactive API docs at:
* **Swagger UI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📁 Project Structure Overview

```text
workplace/
├── app/
│   ├── api/          # Modular API routing endpoints (e.g., users)
│   ├── core/         # Settings loading and config classes
│   ├── database/     # DB session, base models, and seed runners
│   ├── middleware/   # Custom middlewares (CORS, etc.)
│   ├── models/       # SQLAlchemy 2.0 data models (User, Role, etc.)
│   ├── repos/        # Repository layer for database operations
│   ├── services/     # Business logic services
│   └── shared/       # Shared utility helpers (security, etc.)
├── migrations/       # Alembic version control files and environments
├── alembic.ini       # Alembic migration settings
├── main.py           # Application entrypoint
└── req.txt           # Python package requirements
```
