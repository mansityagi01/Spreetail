# Architecture & Design Decisions

## 1. Database & ORM
We used **SQLAlchemy** with a relational SQL schema. SQLite is used for local development out of the box, but the models and queries are 100% compatible with MySQL and PostgreSQL for production deployments (e.g. Render). We chose a relational architecture to properly link Users, Groups, Expenses, Splits, and Settlements, enforcing referential integrity.

## 2. Multi-Currency Strategy
Instead of maintaining multiple floating balances per currency for every user (which is highly complex for the user to understand), we decided on a **Base Currency Approach**. The backend stores the `original_amount` and `currency` of each expense for historical accuracy, but instantly converts the owed amount to a base currency (INR) using a stored `exchange_rate` (e.g. USD 1 = INR 83.00). This perfectly fulfills Aisha's request for "one number per person" while resolving Priya's concern about the inaccurate USD assumption.

## 3. CSV Import Anomalies Policy
Instead of simply dropping dirty data or hardcoding specific lines, we built a generic robust ingestion engine that normalizes inputs and evaluates context:
- **Temporary Users**: If a user is mentioned but not a formal flatmate (e.g., Kabir), they are generated with `is_temporary=True` rather than rejecting the expense.
- **Settlement Detection**: If the notes contain the word "settlement", we bypass the expense creation engine entirely and route the amount to the `Settlements` table, properly adjusting the final net balance.
- **Time-bound Memberships**: By giving `GroupMember` a `joined_at` and `left_at` datetime, we can programmatically drop members like Meera from splits that occur after their move-out date, dynamically recalculating the remaining split shares.

## 4. Frontend Architecture
We used **React with Vite** for lightning-fast compilation. The application is entirely client-side rendered with a centralized `api.js` Axios wrapper. The UI is built with vanilla CSS, maintaining a clean, modern aesthetic with robust error handling via Try/Catch blocks capturing FastAPI's HTTP exceptions.

## 5. Security & Authentication
For this MVP, authentication relies on a simplified login flow where the backend passes the `user_id` as a query parameter. In a full production build, this would be swapped out for JWT bearer tokens in the `Authorization` header. We designed the FastAPI endpoints with `Depends(get_db)` to ensure secure, transaction-bound database sessions.
