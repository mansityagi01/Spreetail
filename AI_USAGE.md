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
