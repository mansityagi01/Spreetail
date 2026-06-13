# AI Context

## Project
Build a Splitwise-inspired expense sharing app as an internship assignment. The app must be a working deployed web app with a public landing page and an authenticated app experience.

## Current Product Understanding
Splitwise helps people track shared expenses, calculate balances, and settle debts. The core value is:
- create groups of people sharing expenses
- add expenses in different split modes
- compute who owes whom
- record payments / settlements
- support discussion on an expense with near-real-time updates

The assignment is not about copying every Splitwise feature. It is about replicating the core behavior needed for a realistic simplified version.

## Agreed MVP Scope So Far
### User and access flow
- Public landing page before sign-in
- Sign-in required to access the app
- Demo login is acceptable (no sign-up flow for MVP)
- After sign-in, user enters the app shell
- Public landing page should closely resemble Splitwise's marketing site in layout, visual style, and tone
- Main CTA on landing page: "Demo Login" only
- Demo users seeded in the system: Mansi, Hari, Puja, Siddh, Nigamasamhita
- No profile/settings page in MVP

### Groups
- Create groups
- Add members manually
- Remove members manually
- All group members have the same permissions (no admin roles)
- When a member is removed from a group, they retain read-only historical access to the group and past expenses

### Expenses
- Two types of expenses are supported:
  - Group expenses (belong to a group and involve multiple group members)
  - Direct 2-person expenses (one-to-one between two users, no group required)
- Support these split types in the MVP:
  - equal
  - unequal
  - percentage
  - shares
- Currency for MVP: Indian Rupees only
- Users can edit and delete expenses
- Expense edits/deletes are controlled by the original creator
- Unequal splits should require exact totals
- File attachments/receipts are supported (basic file upload per expense)

### Balances
- Simplify debts automatically (net off reciprocal debts)
- Show remaining amounts after simplification
- Show group balances and individual balance summary
- Show a detailed balance breakdown, not only the simplified net result
- Display a simplified settlement list showing "who should pay whom" in nettable form

### Settlements
- Manual payments only
- Users can record a payment to settle part or all of a balance
- Payments should update the selected group only

### Expense chat
- Expense-level chat is required
- Near-real-time updates are required (polling or WebSocket, not yet decided)
- Chat should support plain messages for MVP
- Accessible only from the expense detail screen, not from a group activity feed

### UI and public site
- A public landing page is required
- The app does not need to replicate Splitwise’s original marketing site pixel-for-pixel unless later asked
- The product should feel Splitwise-inspired, not a literal clone of the marketing pages
- The app should include these screens in MVP: dashboard/home, group detail, create expense, balances, settlements, and expense chat/comments

## Product Decisions Finalized
- Landing page: Close visual clone of Splitwise (layout, style, tone)
- Demo users: Mansi, Hari, Puja, Siddh, Nigamasamhita (5 accounts)
- Profile/settings: Skipped for MVP
- Removed members: Keep historical read-only access to the group
- Expense types: Two types (group and direct 2-person)
- Notifications: Out of scope for MVP
- Group permissions: All members equal (no admin roles)
- Attachments: Included (basic file upload per expense)
- Settlement view: "Who should pay whom" list only
- Expense chat: Accessible only from expense detail screen

## Implementation Constraints and Preferences
- Use a relational database only
- Keep MVP scope realistic for a 3-day build
- Make the app deployable publicly
- Keep the AI_CONTEXT.md file updated continuously as requirements change
- Before implementation, produce a BUILD_PLAN.md from the agreed context
- The same context should be sufficient for another AI or developer to recreate a similar app

## Prompt That Must Drive the AI Interview
You are a junior engineer helping me complete an internship assignment.
The assignment is to reverse engineer Splitwise, scope a realistic 3-day version,
and build a working deployed app.
Important instructions:
1. Do not assume product requirements.
2. Do not jump directly into implementation.
3. Ask me detailed questions about product scope, UX, workflows, edge cases, and engineering decisions.
4. Ask about every implementation detail needed to build the app.
5. After each answer I give, update a Markdown file called AI_CONTEXT.md.
6. AI_CONTEXT.md must become the source of truth for the entire project.
7. The final app must be buildable from AI_CONTEXT.md.
8. Another evaluator should be able to paste AI_CONTEXT.md into the same AI tool and recreate a similar app.
9. Before writing code, produce a build plan based only on the agreed context.
10. During implementation, keep updating AI_CONTEXT.md whenever requirements, architecture, schema, UI, or logic changes.
11. Do not recommend technical solutions. Your job is to let me think through the technical solution.
Start by interviewing me.
Ask questions across:
- product goals
- Splitwise research
- core workflows
- user personas
- MVP scope
- out-of-scope features
- data model !IMPORTANT!
- authentication
- groups
- expenses
- settlements
- balance calculation
- UI screens
- routing
- frontend architecture
- backend architecture
- database choice
- API design
- deployment
- testing
- known risks
- tradeoffs
Do not give me a final plan until you have asked enough questions.

## Known Tradeoffs So Far
- We will not try to clone the original Splitwise marketing site exactly
- We will keep the MVP limited to one currency
- We will likely simplify the public site and focus on the core app workflows
- We will prioritize balance tracking, split calculation, and settlements over secondary features
- We will use a demo-login approach with seeded accounts instead of real account provisioning for MVP

## Tech Stack (Finalized)
- **Backend**: Python/FastAPI
- **Frontend**: React
- **Database**: MySQL
- **Authentication**: Session-based or simple JWT (dev-friendly approach)
- **Real-time Communication**: WebSocket (Socket.io)
- **API Design**: REST
- **Deployment**: Render.com

## Data Model (Finalized)

### Core Entities
1. **User**
   - id (PK)
   - email (unique, used for demo login)
   - name
   - created_at

2. **Group**
   - id (PK)
   - name
   - description
   - created_by (FK to User)
   - created_at

3. **GroupMember**
   - id (PK)
   - group_id (FK)
   - user_id (FK)
   - is_active (can be removed but keep read-only access)
   - joined_at

4. **Expense**
   - id (PK)
   - group_id (FK, nullable for direct 2-person expenses)
   - payer_id (FK to User, who paid the amount)
   - amount (in Indian Rupees)
   - description
   - created_by (FK to User)
   - created_at
   - updated_at
   - is_deleted (soft delete)
   - expense_type (enum: group, direct_2person)

5. **ExpenseSplit**
   - id (PK)
   - expense_id (FK)
   - user_id (FK, who is involved in this split)
   - split_type (enum: equal, unequal, percentage, shares)
   - split_value (amount or percentage or share count)
   - amount_owed (calculated)

6. **ExpenseAttachment**
   - id (PK)
   - expense_id (FK)
   - file_name
   - file_data (blob/binary)
   - uploaded_at

7. **ExpenseChat**
   - id (PK)
   - expense_id (FK)
   - user_id (FK)
   - message
   - created_at

8. **Balance** (Denormalized for performance, or calculated on the fly)
   - id (PK)
   - user_a_id (FK)
   - user_b_id (FK)
   - group_id (FK, nullable for global 2-person balances)
   - amount (net amount owed by user_a to user_b)
   - last_updated

9. **Settlement**
   - id (PK)
   - from_user_id (FK)
   - to_user_id (FK)
   - group_id (FK, optional if direct 2-person)
   - amount (amount paid)
   - created_at

### Data Model Rules
- Expenses have a payer (who paid) and splitters (participants who share the cost)
- Split types: equal (divide equally), unequal (fixed amounts), percentage (%, sum = 100), shares (fixed shares)
- Balances are simplified (net off reciprocal debts)
- Direct 2-person expenses contribute to global balance between those users
- Removed group members retain read-only access to historical expenses
- Settlements reduce the owed amount between users in a group
- File attachments stored as binary data in the database

## Next Step
All product and technical decisions are finalized. Now produce BUILD_PLAN.md and begin implementation.

## Implementation Progress Log

### Completed in this implementation session
- Backend scaffold created at `backend/app`
- FastAPI app bootstrapped with CORS and health routes
- SQLAlchemy models implemented for users, groups, memberships, expenses, splits, chats, attachments, balances, settlements
- Demo auth implemented:
   - `GET /api/auth/demo-users`
   - `POST /api/auth/demo-login`
- Group APIs implemented:
   - create group
   - list groups by user
   - get group detail
   - add member
   - soft-remove member
- Expense APIs implemented:
   - create, get, edit, soft-delete expense
   - expense chat read/post
- Balance/settlement APIs implemented:
   - global balances
   - group balances
   - simplified `who should pay whom` settlement list
   - record settlement/payment
- Frontend scaffold created at `frontend/` with React + Vite
- Public landing page implemented with demo login flow
- Authenticated app shell implemented with navigation
- Dashboard implemented for:
   - creating groups
   - adding members
   - creating expenses
- Group page implemented for:
   - member list
   - group balances
   - group expenses list
- Expense detail page implemented with expense chat
- Settlements page implemented to:
   - view simplified settlement list
   - record manual payments

### Important architecture updates during implementation
- Real-time expense chat implemented as polling every 3 seconds for MVP (near-real-time), not WebSocket yet
- Local development DB currently defaults to SQLite via fallback `DATABASE_URL` for speed; relational DB requirement still satisfied
- Production target remains MySQL by setting `DATABASE_URL` to MySQL connection string

### Implemented API contract notes
- Most write operations use `user_id` as query parameter for simplified demo auth context
- Group member add currently expects `new_user_id` as query param
- Settlement list endpoint currently returns computed net instructions and user display names

## Known Limitations (Current Build)
- No full session/JWT security yet; demo auth only
- No WebSocket transport yet for chat; uses short polling
- Expense attachment upload UI/API persistence path is modeled but upload endpoint is not completed yet
- Dashboard expense form currently uses user IDs for split input (usability tradeoff for speed)
- No automated tests added yet in this session
