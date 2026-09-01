# Finx Pulse Backend

Backend API for **Finx Pulse**, a modern financial platform.

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Docker

## Getting Started

### 1. Clone

```bash
git clone https://github.com/MadChief815/FinX-Pulse-Backend.git
cd finx-pulse-backend
```

### 2. Environment

```bash
cp .env.example .env
```

Configure the required environment variables in `.env`.

### 3. Start PostgreSQL

```bash
docker compose up -d postgres
```

### 4. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start server

```bash
python manage.py runserver
```

API: `http://127.0.0.1:8000`

## Backend

This backend requires the **Finx Pulse Frontend**:

https://github.com/MadChief815/FinX-Pulse-Frontend
