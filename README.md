# Spreetail (Shared Expenses App)

A full-stack web application built to cleanly track, split, and settle shared expenses amongst friends and flatmates. Built specifically to resolve chaotic spreadsheet histories with robust data sanitization, multi-currency support, and transparent itemized balances.

## Features

- **Robust CSV Import**: Upload a messy spreadsheet (`expenses_export.csv`) and the AI-driven data parser will automatically clean it, resolving 15 unique anomalies including missing currencies, duplicate rows, dates written in various formats, and percentage splits exceeding 100%.
- **Multi-Currency Support**: Add expenses in USD, and they will automatically map to INR for a seamless, unified ledger balance.
- **Itemized Breakdowns**: Stop guessing where a balance came from. View a chronological, itemized receipt between any two users showing exactly which expenses and settlements led to the final number.
- **Time-Bound Memberships**: Handles move-ins and move-outs by ensuring people aren't billed for expenses when they didn't live there.
- **File Attachments**: Upload and download receipt images (up to 5MB) directly onto specific expenses.

## Tech Stack

- **Backend**: Python 3, FastAPI, SQLAlchemy ORM, SQLite (local) / MySQL (production)
- **Frontend**: React.js, Vite, Axios
- **Styling**: Modern, responsive vanilla CSS

## Getting Started

### Prerequisites
- Node.js (v16+)
- Python 3.9+
- pip

### 1. Run the Backend
Open a terminal and navigate to the `backend` directory.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The FastAPI documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

### 2. Run the Frontend
Open a new terminal and navigate to the `frontend` directory.

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```
The React app will automatically open at `http://localhost:5173`.

## Usage Guide
1. **Login**: The app starts with a quick demo login screen. Select "Aisha" or any other flatmate to enter.
2. **Import Data**: Click **Import Data** in the top navigation. Upload the `expenses_export.csv` file. You will be presented with a full anomaly resolution report.
3. **View Balances**: Go to the **Balances** tab to see who owes who. Click **View Breakdown** to see the itemized list of expenses.
4. **Settle Up**: Go to **Settlements** to log a payment and clear a debt.

## Project Deliverables
For architectural decisions, scope details, and AI usage information, please see the included markdown files.

**AI Tool Used**: This project was developed alongside an advanced LLM coding assistant (Antigravity), which orchestrated backend boilerplate, generated the robust 15-case CSV regex parsing engine, and styled the frontend. 

- `SCOPE.md`: Contains the exact data anomalies found in the CSV and the database schema.
- `DECISIONS.md`: The log of major architectural and product decisions.
- `AI_USAGE.md`: Detailed prompts and the 3 concrete cases where the AI got things wrong and had to be corrected.
