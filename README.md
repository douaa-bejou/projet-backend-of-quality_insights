# Quality Insights Backend

FastAPI backend for quality insights.

## Quick Start (SQLite + Uvicorn, recommended)

1. Create `.env` from `.env.example`.

```env
DATABASE_URL=sqlite:///./quality_insights_local.db
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173
BOOTSTRAP_ADMIN_NAME=Responsable
BOOTSTRAP_ADMIN_EMAIL=admin@gmail.com
BOOTSTRAP_ADMIN_PASSWORD=ChangeMe123!
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. Check health:

```bash
curl http://127.0.0.1:8000/health
```

## Deploy on Render (recommended for access from any PC)

1. Push this backend folder to GitHub.

2. In Render:
- `New +` -> `PostgreSQL`.
- Create database (example name: `quality-insights-db`).

3. In Render:
- `New +` -> `Web Service` -> connect your GitHub repo.
- If backend is in a subfolder, set `Root Directory` to that folder path.

4. Configure service:
- Environment: `Python 3`
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Add Environment Variables in Render:
- `DATABASE_URL` = PostgreSQL connection string from your Render database
- `SECRET_KEY` = long random string
- `CORS_ORIGINS` = your frontend URL (example `https://analysescrap-hutchinson.vercel.app`)
- `BOOTSTRAP_ADMIN_NAME` = `Responsable`
- `BOOTSTRAP_ADMIN_EMAIL` = your admin email
- `BOOTSTRAP_ADMIN_PASSWORD` = strong password

6. Deploy and test:
- Health endpoint:

```text
https://YOUR_RENDER_SERVICE/health
```

- API root example:

```text
https://YOUR_RENDER_SERVICE/api/v1
```

7. In Vercel frontend, set:

```env
VITE_API_BASE_URL=https://YOUR_RENDER_SERVICE/api/v1
```

Then redeploy frontend.

## Multi-PC / LAN Access

- Start backend on the server PC with `--host 0.0.0.0 --port 8000`.
- On the client PC, use `http://<SERVER_IP>:8000/api/v1` as frontend API base URL.
- Ensure firewall allows inbound TCP `8000` on the server PC.
- CORS accepts localhost and private LAN ranges (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`).

## MySQL mode (for production-like environment)

Use `.env.mysql.example` as a base and make sure MySQL is running on `localhost:3306`.

## Docker Compose (DB + API)

```bash
docker compose up --build
```

Then API is available on `http://127.0.0.1:8000` (and on `http://<SERVER_IP>:8000` in LAN).
