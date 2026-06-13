# BUILD_PLAN.md

## 1. Product Research

### How We Studied Splitwise
- Read the Splitwise company/team page for context on the product vision and focus on "fairness"
- Identified core workflows: group creation, expense tracking, balance calculation, settlement
- Reviewed the product statement: "organize shared expenses and IOUs"

### What We Learned
- Splitwise is fundamentally a ledger + balance calculator
- The core value is simplifying who owes whom
- Three use cases identified: roommates, trips, friends, general shared costs
- Splitwise focuses on fairness as a differentiator (beyond just accounting)

### Workflows Identified
1. **Group Setup**: Create group → add members → start sharing expenses
2. **Expense Tracking**: Add expense → assign payer → split among group → record as balance
3. **Balance Calculation**: Net off reciprocal debts → show who owes whom
4. **Settlement**: Record manual payments → reduce balances

### Product Assumptions Made
- MVP does not need fairness calculators or advice features
- MVP does not need recurring expenses, itemization, or payment integrations
- We optimize for simplicity of the core workflows, not maximum feature parity
- We support both group expenses and direct 2-person expenses
- We assume demo login is acceptable for internship submission

## 2. Architecture

### Tech Stack
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend | Python/FastAPI | Fast to build, async support for WebSocket, good ORM options |
| Frontend | React | Standard, rich ecosystem, good for real-time chat with Socket.io |
| Database | MySQL | Relational, reliable, supports complex queries for balance calculation |
| Authentication | Session-based (dev-friendly) | Simpler than full JWT for demo login scenario |
| Real-time | Socket.io (WebSocket) | Near-real-time expense chat with fallback to polling |
| Deployment | Render.com | Cheap, easy deployment for full-stack app |

### Database Schema
See AI_CONTEXT.md for detailed entity definitions. Key tables:
- **users**: Demo login accounts
- **groups**: Expense groups
- **group_members**: Membership with soft removal tracking
- **expenses**: Both group and direct 2-person expenses
- **expense_splits**: Payer and split participants
- **expense_attachments**: File uploads (binary data)
- **expense_chat**: Expense-level comments/messages
- **balances**: Simplified net balances (may be denormalized or calculated)
- **settlements**: Payment records that reduce balances

### API Design (REST)

#### Authentication
```
POST /api/auth/demo-login
  body: { email: "mansi@splitwise.app" }
  response: { user_id, session_token }
```

#### Users
```
GET /api/users - list all users (for group member selection)
GET /api/users/:id - user profile
```

#### Groups
```
POST /api/groups - create group
GET /api/groups - user's groups
GET /api/groups/:id - group detail with members
POST /api/groups/:id/members - add member
DELETE /api/groups/:id/members/:user_id - remove member
```

#### Expenses
```
POST /api/expenses - create expense (group or direct 2-person)
  body: { 
    payer_id, amount, description, expense_type, 
    splits: [{ user_id, split_type, split_value }],
    group_id (optional)
  }
GET /api/expenses/:id - expense detail + chat
GET /api/expenses/:id/chat - expense chat messages
POST /api/expenses/:id/chat - post chat message (triggers Socket.io emit)
PATCH /api/expenses/:id - edit expense (creator only)
DELETE /api/expenses/:id - delete expense (creator only)
```

#### Balances & Settlements
```
GET /api/balances - global balance summary for logged-in user
GET /api/groups/:id/balances - group-specific balances
GET /api/settlements - simplified "who pays whom" list

POST /api/settlements - record payment
  body: { from_user_id, to_user_id, amount, group_id (optional) }
```

### Frontend Structure
```
/src
  /pages
    Landing.jsx (Splitwise-like homepage)
    Dashboard.jsx (authenticated home, list groups & recent expenses)
    GroupDetail.jsx (group members, expenses, balances)
    CreateExpense.jsx (form for new expense, split types)
    ExpenseDetail.jsx (expense info, chat widget, edit/delete)
    BalancesPage.jsx (group and global balances, settlement list)
    SettlementsPage.jsx (record payments, payment history)
  
  /components
    GroupCard.jsx
    ExpenseCard.jsx
    SplitTypeSelector.jsx
    BalanceSummary.jsx
    ChatWidget.jsx (WebSocket listener)
    AttachmentUpload.jsx
  
  /hooks
    useAuth.js (session management)
    useSocket.js (Socket.io connection)
    useFetch.js (API calls)
  
  /utils
    api.js (REST client)
    balanceCalculator.js (split logic)
```

### Backend Structure
```
/app
  main.py (FastAPI entry point)
  
  /models
    user.py
    group.py
    expense.py
    balance.py
    settlement.py
  
  /routes
    auth.py
    users.py
    groups.py
    expenses.py
    balances.py
    settlements.py
  
  /schemas
    user.py
    group.py
    expense.py
    (Pydantic schemas for validation)
  
  /services
    balance_service.py (calculate, simplify, net off)
    expense_service.py (create, update, delete, split logic)
    settlement_service.py (record payment, reduce balance)
    attachment_service.py (file upload/retrieval)
  
  /utils
    database.py
    auth.py (session/token handling)
    socket_manager.py (Socket.io event handlers)
  
  /seed
    demo_data.py (seed 5 demo users and sample expenses)
```

### Frontend Architecture
- React with hooks (no Redux for MVP simplicity)
- Socket.io client for real-time chat updates
- Fetch API for REST calls
- Tailwind CSS or Material-UI for styling (Splitwise-inspired)

### Deployment Approach
1. Backend deployed to Render.com (Node.js or Python environment)
2. Frontend deployed to Render.com (static site or Node.js server)
3. MySQL database on Render or managed MySQL service (e.g., PlanetScale, AWS RDS free tier)
4. Environment variables for API endpoints, database connection

## 3. AI Collaboration Process

### Initial Instructions
We used the required initial prompt from the assignment:
- Positioned AI as a junior engineer, not a prompt engineer
- Emphasized no assumption of requirements
- Required detailed questions before any implementation
- Mandated AI_CONTEXT.md as the source of truth

### Questions the AI Asked (Batched Interviews)

**Batch 1 - Product Decisions:**
1. Primary user persona (chose: general mixed use)
2. Landing page scope (chose: full visual clone)
3. Demo login approach (chose: preset accounts)
4. Group member management (manual add/remove only)
5. Debt simplification (automatic + show remaining)
6. Real-time chat (near-real-time, not instant)
7. Split types (all four in MVP)
8. Currency (INR only)
9. Expense editing (original creator only)
10. Settlement type (manual payments)

**Batch 2 - UX & Features:**
1. Landing page structure (Splitwise close visual clone)
2. Required screens (dashboard, group detail, create expense, balances, settlements, chat)
3. Removed member visibility (retain read-only access)
4. Expense types (both group and direct 2-person)
5. Balance display (detailed breakdown + settlement list)
6. Chat location (expense detail only)
7. Attachment support (included)

**Batch 3 - Tech Stack:**
1. Backend (chose: Python/FastAPI)
2. Frontend (chose: React)
3. Database (chose: MySQL)
4. Auth (chose: session-based)
5. Real-time (chose: WebSocket/Socket.io)
6. Deployment (chose: Render.com)
7. API design (chose: REST)

**Batch 4 - Data Model:**
1. Login field (email)
2. Payer vs. splitter distinction (yes)
3. Balance storage (raw transactions + net balances)
4. Direct expense global balance (yes, contributes)
5. Settlement reduces balance (yes, clear debt)
6. File storage (database as blob)

### How We Answered
- Gave direct, concise answers without over-explaining reasoning
- Made decisive choices for clear scope (e.g., INR only, MySQL only, no admin roles)
- Prioritized simplicity and 3-day buildability in all decisions
- Chose seeded demo users (Mansi, Hari, Puja, Siddh, Nigamasamhita) to feel realistic

### How the Plan Evolved
1. **Start**: Vague understanding of Splitwise, multiple possible feature sets
2. **After Batch 1**: Core workflows defined, split types locked, currency fixed
3. **After Batch 2**: Exact screens, expense types, and balance display decided
4. **After Batch 3**: Tech stack committed, no room for framework changes mid-build
5. **After Batch 4**: Schema defined, balance calculation logic documented
6. **Final**: AI_CONTEXT.md became the single source of truth; no more questions

### AI_CONTEXT.md Maintenance
- Created on first pass with initial scope
- Updated after each batch of questions with finalized decisions
- Evolved from vague product assumptions to detailed schema and deployment plan
- Now serves as the complete blueprint for implementation
- Will be continuously updated as actual implementation reveals changes

## 4. Tradeoffs

### What We Simplified
| Feature | Original Splitwise | Our MVP | Reason |
|---------|-------------------|---------|--------|
| Signup | Full email signup + verification | Demo login with seeded users | 3-day timeline |
| Currencies | 100+ currencies | INR only | Scope control |
| Split types | Advanced (itemization, custom) | 4 basic types | Covers most use cases |
| Fairness advice | Crowdsourced fairness calculators | None | Complex to build |
| Mobile | iOS + Android native apps | Web only | Time constraint |
| Payments | Direct payment processing | Manual record only | Payment integration complex |
| Recurring | Recurring expense templates | One-off only | Not core MVP |
| Notifications | Push + email + SMS | None | Out of scope |
| Profiles | Detailed user profiles | Skipped | Not essential |
| Admin roles | Group owner + permissions | All members equal | Simplifies UX |

### What We Hardcoded
- Demo user list (5 users fixed)
- Currency (INR hardcoded, no conversion)
- Deployment target (Render.com assumed)
- Landing page structure (Splitwise-inspired template)

### What We Avoided
- Third-party payment integrations (Stripe, PayPal)
- Email or SMS notifications
- Mobile app (web only)
- Multi-tenant admin dashboards
- Advanced analytics or graphs
- Expense itemization (single amount per expense)
- Currency conversion
- Real-time notifications (only chat is real-time)

### What We Would Improve With More Time
1. **Production Auth**: Replace demo login with real email signup + OAuth
2. **Payment Integration**: Stripe or Razorpay to enable actual settlement payments
3. **Mobile App**: React Native or native iOS/Android
4. **Notifications**: Email or push notifications for balance changes or payments
5. **Multiple Currencies**: Support exchange rates and conversion
6. **Offline Mode**: Service workers for offline access
7. **Advanced Splits**: Itemized expenses, receipt OCR
8. **Analytics**: Charts, spending trends, category breakdowns
9. **Fairness Features**: Crowdsourced fairness advice, dispute resolution
10. **Admin Features**: Group owner controls, member permissions, audit logs

## 5. Implementation Timeline (3 Days)

### Day 1: Backend + Database
- [ ] Set up FastAPI project, MySQL schema, alembic migrations
- [ ] Implement demo login, user endpoints
- [ ] Implement groups and members endpoints
- [ ] Seed 5 demo users with sample groups

### Day 2: Expense Logic + Balances
- [ ] Implement expense creation with all split types
- [ ] Implement expense update/delete (creator only)
- [ ] Implement balance calculation and simplification
- [ ] Implement settlement recording
- [ ] Implement expense attachments

### Day 3: Frontend + Real-time Chat
- [ ] Set up React project, routing
- [ ] Build landing page (Splitwise-inspired)
- [ ] Build dashboard, group detail, expense detail screens
- [ ] Implement expense chat with Socket.io
- [ ] Deploy to Render, test all workflows

## 6. Success Criteria for MVP
- [ ] Landing page accessible and resembles Splitwise
- [ ] Demo login works for all 5 seeded users
- [ ] Can create groups, add/remove members
- [ ] Can create expenses with all 4 split types
- [ ] Balance calculation is correct (verified with manual math)
- [ ] Expense chat works with near-real-time updates
- [ ] Can record settlements and see updated balances
- [ ] Can edit and delete own expenses
- [ ] Deployed to public URL
- [ ] README.md with setup instructions
- [ ] GitHub repository with clean commit history
- [ ] AI_CONTEXT.md fully documented
- [ ] BUILD_PLAN.md complete
- [ ] Key prompts collected and documented

## 7. Known Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Balance calc bugs | Wrong debts, app unusable | Unit test balance logic, verify manually |
| Real-time updates fail | Chat doesn't work | Fallback to polling, simple HTTP refresh |
| Deployment issues | App not public | Use Render.com managed services, test deploy early |
| File upload size | Large files break | Limit to 5MB, store efficiently |
| Demo login collision | Users interfere | Use unique session management per browser |
| Schema mismatch | API/DB incompatible | Generate migrations early, validate schema |

---

**Status**: Ready for implementation.
**Approval**: Product scope frozen. No more product changes without explicit request.
**Next**: Start Day 1 backend setup.
