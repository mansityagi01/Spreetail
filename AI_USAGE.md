# AI Usage Statement

This project was built using an advanced LLM coding assistant (Antigravity).

## Code Generation
- The FastAPI backend router structure, SQLAlchemy ORM models, and Pydantic schemas were largely orchestrated by AI, following architectural guidelines and best practices.
- The `import_csv.py` endpoint was developed by identifying the 15 anomalies through AI-driven data analysis of `expenses_export.csv` and iteratively building Python logic to parse, sanitize, and persist the records into the database.
- The React frontend structure, including state management (`useState`, `useEffect`) and the Axios API layer, was generated and refined by AI.
- The CSS (`index.css`) was styled via AI to provide a modern, minimalist interface.

## Debugging and Refactoring
- The AI debugger was utilized to trace asynchronous issues between the frontend and backend, particularly handling FastAPIs strict Pydantic validation (e.g. tracking down 422 Unprocessable Entity errors when missing `original_amount` during POSTs).
- Refactoring the `balances_service.py` to support an itemized breakdown for the new `BalanceBreakdownPage.jsx` was driven entirely by an AI subagent reviewing the existing reciprocal debt logic.

## AI Impact
- Using an AI coding assistant accelerated the development cycle significantly, especially in scaffolding boilerplate (React Router, FastAPI app structure) and writing the tedious regex and formatting rules required for a 15-case robust CSV parsing engine. The system's ability to recursively verify its own schema changes against frontend API calls prevented integration bugs before they ran.

## Concrete AI Failures & Corrections

**1. Vercel Ephemeral File System**
- **What went wrong**: The AI generated code to fall back to a local SQLite database (`sqlite:////tmp/splitwise.db`) if a PostgreSQL connection string wasn't provided. 
- **How I caught it**: The database appeared to work initially (e.g. logging in seeded the users), but navigating to a new page immediately threw a 404 error because the data vanished. I realized Vercel Serverless Functions spin up new ephemeral instances per request.
- **What I changed**: I realized a persistent database was strictly necessary. I retained the `POSTGRES_URL` code and manually provisioned and linked a Vercel Postgres (Neon) database through the Vercel dashboard.

**2. Middleware Host Blocking**
- **What went wrong**: The AI generated a security `TrustedHostMiddleware` for FastAPI that hardcoded the allowed hosts to `localhost` and `render.com`.
- **How I caught it**: The deployed Vercel frontend failed to fetch users, receiving a `400 Bad Request` from the backend.
- **What I changed**: I modified `app/main.py` to include `*.vercel.app` and a wildcard `*` in the `allowed_hosts` array.

**3. Vercel Route Prefix Stripping**
- **What went wrong**: The AI configured Vercel `experimentalServices` where the backend was prefixed with `/api`. However, Vercel automatically stripped this prefix before forwarding the request to Python, meaning FastAPI (which expected `/api/auth/demo-users`) received `/auth/demo-users`.
- **How I caught it**: The browser console showed a `404 Not Found` for API endpoints, even though they were defined correctly in the Python routers.
- **What I changed**: I restructured `vercel.json` to assign the backend service a dummy prefix (`/_backend`) and used a global rewrite rule (`"source": "/api/(.*)", "destination": "/_backend/api/$1"`) to trick Vercel into preserving the `/api` path.
