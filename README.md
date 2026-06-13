# Spreetail — Expense Sharing App

A **Splitwise-inspired** expense sharing web application built as an internship assignment. Track shared expenses, split bills fairly, and settle debts with friends.

> **Live Demo**: _Deploy to [Render.com](https://render.com) using the included `render.yaml`._

---

## Features

| Feature | Description |
|---------|-------------|
| **Demo Login** | Pick from 5 pre-seeded users — no signup needed |
| **Groups** | Create groups, add/remove members |
| **Expenses** | Add group or direct 2-person expenses |
| **4 Split Types** | Equal, unequal, percentage, and shares-based splitting |
| **Smart Balances** | Automatic pairwise debt simplification |
| **Settlements** | Record manual payments to settle debts |
| **Expense Chat** | Near-real-time comment threads on each expense (3s polling) |
| **File Attachments** | Upload receipts or files to any expense |

### Demo Users

| Name | Email |
|------|-------|
| Mansi | mansi@splitwise.app |
| Hari | hari@splitwise.app |
| Puja | puja@splitwise.app |
| Siddh | siddh@splitwise.app |
| Nigamasamhita | nigamasamhita@splitwise.app |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 + Vite |
| **Backend** | Python / FastAPI |
| **Database** | SQLite (dev) / MySQL (prod) |
| **ORM** | SQLAlchemy 2.0 |
| **Validation** | Pydantic v2 |
| **HTTP Client** | Axios |
| **Deployment** | Render.com |

---

## Getting Started

### Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/mansityagi01/Spreetail.git
cd Spreetail
```

### 2. Set Up the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger documentation.

### 3. Set Up the Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The app will be available at `http://localhost:5173`.

### 4. Use the App

1. Open `http://localhost:5173` in your browser
2. Select a demo user from the dropdown and click **Demo Login**
3. Create a group and add other demo users as members
4. Create expenses with any of the 4 split types
5. View balances and settle debts
6. Open any expense to chat and upload attachments

---

## Project Structure

```
Spreetail/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point, CORS, routers
│   │   ├── database.py          # SQLAlchemy engine & session setup
│   │   ├── models/
│   │   │   └── models.py        # 9 SQLAlchemy ORM models
│   │   ├── routes/
│   │   │   ├── auth.py          # Demo login endpoints
│   │   │   ├── users.py         # User listing endpoints
│   │   │   ├── groups.py        # Group CRUD + member management
│   │   │   ├── expenses.py      # Expense CRUD + chat + attachments
│   │   │   └── balances.py      # Balance calculation + settlements
│   │   ├── schemas/
│   │   │   └── schemas.py       # Pydantic request/response schemas
│   │   └── services/
│   │       └── balance_service.py  # Split calc + debt simplification
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # React Router + auth guard
│   │   ├── api.js               # Axios client config
│   │   ├── index.css            # Complete design system
│   │   ├── components/
│   │   │   └── Layout.jsx       # App shell (nav bar + logout)
│   │   └── pages/
│   │       ├── LandingPage.jsx  # Public landing + demo login
│   │       ├── DashboardPage.jsx # Groups + create expense
│   │       ├── GroupPage.jsx    # Group detail + members + balances
│   │       ├── ExpensePage.jsx  # Expense detail + chat + attachments
│   │       ├── BalancesPage.jsx # Global balance summary
│   │       └── SettlementsPage.jsx # Settlement recording
│   ├── package.json
│   └── vite.config.js
│
├── AI_CONTEXT.md                # Complete project requirements (source of truth)
├── BUILD_PLAN.md                # Architecture & implementation plan
├── KEY_PROMPTS.md               # AI prompts used during development
└── render.yaml                  # Render.com deployment config
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/demo-users` | List available demo accounts |
| POST | `/api/auth/demo-login` | Login with demo email |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users |
| GET | `/api/users/{id}` | Get user by ID |

### Groups
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/groups` | Create a group |
| GET | `/api/groups` | List user's groups |
| GET | `/api/groups/{id}` | Group detail with members & expenses |
| POST | `/api/groups/{id}/members` | Add a member |
| DELETE | `/api/groups/{id}/members/{uid}` | Remove a member (soft delete) |

### Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/expenses` | Create expense with splits |
| GET | `/api/expenses/{id}` | Get expense detail |
| PATCH | `/api/expenses/{id}` | Update expense (creator only) |
| DELETE | `/api/expenses/{id}` | Soft-delete expense (creator only) |

### Expense Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expenses/{id}/chat` | Get chat messages |
| POST | `/api/expenses/{id}/chat` | Post a message |

### Attachments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/expenses/{id}/attachments` | Upload file (max 5MB) |
| GET | `/api/expenses/{id}/attachments` | List attachments |
| GET | `/api/expenses/attachments/{id}/download` | Download attachment |

### Balances & Settlements
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/balances` | Global balance summary |
| GET | `/api/groups/{id}/balances` | Group-specific balances |
| GET | `/api/settlements` | Simplified "who pays whom" list |
| POST | `/api/settlements` | Record a payment |

---

## Data Model

```
User ──< GroupMember >── Group
  │                        │
  ├──< Expense ────────────┘
  │      ├──< ExpenseSplit
  │      ├──< ExpenseChat
  │      └──< ExpenseAttachment
  │
  └──< Settlement
```

### Split Types

| Type | How It Works |
|------|-------------|
| **Equal** | Total ÷ number of participants |
| **Unequal** | Fixed amounts per person (must sum to total) |
| **Percentage** | Percentage per person (must sum to 100%) |
| **Shares** | Proportional shares (e.g., 2:1:1 ratio) |

---

## Deployment (Render.com)

The project includes a `render.yaml` for one-click deployment:

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New** → **Blueprint**
4. Connect your GitHub repo
5. Render will auto-detect `render.yaml` and create:
   - Backend web service (Python)
   - Frontend static site
6. Set the `DATABASE_URL` environment variable for MySQL (or leave empty for SQLite)
7. Set `VITE_API_URL` to your backend's Render URL

### Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | MySQL connection string (optional, defaults to SQLite) |
| `VITE_API_URL` | Frontend | Backend API URL (e.g., `https://spreetail-backend.onrender.com`) |

---

## Design Decisions & Tradeoffs

| Decision | Rationale |
|----------|-----------|
| Demo login (no signup) | 3-day timeline; acceptable for internship |
| INR only (no multi-currency) | Scope control for MVP |
| Polling instead of WebSocket | Simpler; 3s polling is sufficient for demo |
| SQLite for dev | Zero setup; MySQL for production |
| Pairwise debt simplification | Covers most use cases; full graph optimization deferred |
| File attachments as BLOB | Simple for MVP; S3/cloud storage for production |

---

## Known Limitations

- **No real authentication** — demo login only (no passwords, JWT, or sessions)
- **No push notifications** — out of MVP scope
- **Chat uses HTTP polling** (3s interval), not WebSocket
- **Single currency** (INR) — no multi-currency or conversion
- **No automated tests** — documented as future improvement
- **File attachments stored in DB** — not suitable for large files in production

---

## Built With

This project was built through an **AI-assisted development process**:

1. **Product Interview** — Structured Q&A to scope features (documented in `AI_CONTEXT.md`)
2. **Build Plan** — Architecture and schema design (documented in `BUILD_PLAN.md`)
3. **Implementation** — Iterative development with continuous context updates
4. **Key Prompts** — Development prompts documented in `KEY_PROMPTS.md`

The `AI_CONTEXT.md` file serves as the **single source of truth** — another developer can use it to recreate a similar application.

---

## License

This project was built as an internship assignment and is not licensed for commercial use.
