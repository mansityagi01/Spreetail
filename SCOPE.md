# Spreetail Scope Document

## Completed Features

### 1. Robust CSV Importer (The 15 Anomalies)
The application includes a specialized `POST /api/import` endpoint that parses the provided `expenses_export.csv` and automatically corrects the 15 deliberate data anomalies:
1. **Date Format Chaos**: Normalized mm/dd/yyyy, dd/mm/yyyy, and textual dates. Fixed "04/05/2026" based on trip context.
2. **Unknown Members**: Added non-regular members (e.g., Kabir) as `is_temporary=True` guests so they can participate without a permanent account.
3. **Name Inconsistencies**: Fuzzy matching and stripping (e.g., "Priya S" -> "Priya", "rohan " -> "Rohan").
4. **Zero Amount**: Safely skipped 0-amount entries.
5. **Commas & Spaces in Amounts**: Stripped non-numeric characters before parsing as float.
6. **Negative Amounts**: Treated as refunds / negative expenses.
7. **Rounding Issues**: Forced amounts to 2 decimal places.
8. **Missing Currency**: Defaulted to INR when blank.
9. **Multi-Currency (USD/INR)**: Extracted original USD values, stored them, and converted to INR at a rate of 83.00 for unified global balances.
10. **Settlements as Expenses**: Detected "settlement" in the notes and converted the row to a direct `Settlement` entity instead of a shared expense.
11. **Exact Duplicates**: Tracked rows by date, amount, and payer to discard exact duplicate rows.
12. **Conflicting Duplicates**: Kept the higher amount when two similar entries conflicted.
13. **Percentages > 100%**: Normalized percentage splits proportionally so they always sum to exactly 100%.
14. **Left Member Included**: Handled time-bound memberships by removing Meera from April expenses (after she moved out) and redistributing her share.
15. **Split Type Mismatch**: Corrected `equal` type when unequal details (like percentages or shares) were provided.

### 2. Multi-Currency Support
The system tracks `original_amount`, `currency`, and `exchange_rate` allowing the underlying balances engine to always sum the primary currency (INR) while preserving the original context.

### 3. Time-Bounded Memberships
The `GroupMember` schema tracks `joined_at` and `left_at`. The importer utilizes this to automatically exclude users from expenses that occur when they were not part of the group.

### 4. Itemized Balance Breakdown
Fulfilling Rohan's request ("No magic numbers"), the app features a `View Breakdown` page that fetches all expenses and settlements between two users, sorting them chronologically to show exactly how the net balance was derived.

### 5. File Attachments
Implemented the backend API (`/api/expenses/{id}/attachments`) and frontend components for uploading and downloading expense receipts up to 5MB.

### 6. Interactive UX
The app includes a fully integrated dashboard with real-time balance calculations, direct chat messaging per expense, and a dedicated CSV Import Wizard that displays a detailed anomaly detection report.

## Database Schema

We use a normalized SQL schema managed by SQLAlchemy. 

- **users**: Core identity. `id`, `email`, `name`, `is_temporary` (for guests like Kabir).
- **groups**: Represents shared contexts. `id`, `name`, `description`.
- **group_members**: Links users to groups with a time-bound state. `group_id`, `user_id`, `joined_at`, `left_at` (used for detecting past memberships).
- **expenses**: Core transactional record. `id`, `group_id`, `payer_id`, `amount`, `currency`, `original_amount`, `exchange_rate`, `expense_type` (group or direct_2person).
- **expense_splits**: Records exactly how an expense is divided. `expense_id`, `user_id`, `split_type` (equal, unequal, percentage, shares), `split_value`, `amount_owed`.
- **settlements**: Direct payments to clear debt. `from_user_id`, `to_user_id`, `amount`.
- **expense_attachments**: File storage for receipts. `expense_id`, `file_name`, `file_data` (BLOB).
- **expense_chats**: Threaded discussion per expense. `expense_id`, `user_id`, `message`.
- **import_logs & anomalies**: Tracks the CSV ingestion results for accountability.
