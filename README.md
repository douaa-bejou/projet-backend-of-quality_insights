# Quality Insights Backend

FastAPI backend for quality insights.

## Local run (SQLite + Uvicorn, recommended for quick start)

1. Create `.env`:

```env
DATABASE_URL=sqlite://
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173
BOOTSTRAP_ADMIN_NAME=Responsable
BOOTSTRAP_ADMIN_EMAIL=admin@gmail.com
BOOTSTRAP_ADMIN_PASSWORD=ChangeMe123!
```

`sqlite://` runs an in-memory DB (no MySQL needed, no file lock issues).

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Check health:

```bash
curl http://127.0.0.1:8000/health
```

## MySQL mode (for production-like environment)

Use `.env.mysql.example` as a base and make sure MySQL is running on `localhost:3306`.

## Docker Compose (DB + API)

```bash
docker compose up --build
```

Then API is available on `http://127.0.0.1:8000`.
