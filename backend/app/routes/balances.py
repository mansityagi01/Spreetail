from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Expense, ExpenseSplit, Group, GroupMember, Settlement, User
from app.services.balance_service import simplify_debts
from app.schemas.schemas import SettlementCreate, SettlementResponse

router = APIRouter(prefix="/api", tags=["balances", "settlements"])


def build_raw_debts(db: Session, group_id: int = None):
    """Build raw debts as mapping of (from_user_id, to_user_id) -> amount owed."""
    query = db.query(Expense).filter(Expense.is_deleted == False)
    if group_id is not None:
        query = query.filter(Expense.group_id == group_id)

    expenses = query.all()
    debts = {}

    for expense in expenses:
        for split in expense.splits:
            if split.user_id == expense.payer_id:
                continue

            key = (split.user_id, expense.payer_id)
            debts[key] = debts.get(key, 0.0) + float(split.amount_owed)

    # Apply settlements to reduce debts
    settlement_query = db.query(Settlement)
    if group_id is not None:
        settlement_query = settlement_query.filter(Settlement.group_id == group_id)

    settlements = settlement_query.all()
    for settlement in settlements:
        pay_key = (settlement.from_user_id, settlement.to_user_id)
        current = debts.get(pay_key, 0.0)
        remaining = current - float(settlement.amount)

        if remaining >= 0:
            debts[pay_key] = remaining
        else:
            debts[pay_key] = 0.0
            reverse_key = (settlement.to_user_id, settlement.from_user_id)
            debts[reverse_key] = debts.get(reverse_key, 0.0) + abs(remaining)

    debts = {k: v for k, v in debts.items() if v > 0.01}
    return simplify_debts(debts)


@router.get("/balances")
def get_global_balances(user_id: int, db: Session = Depends(get_db)):
    """Get global balance summary for the logged-in user across all groups and direct expenses"""
    simplified = build_raw_debts(db)
    user_balances = {}

    for (from_user_id, to_user_id), amount in simplified.items():
        if from_user_id == user_id:
            user_balances[to_user_id] = user_balances.get(to_user_id, 0.0) - amount
        if to_user_id == user_id:
            user_balances[from_user_id] = user_balances.get(from_user_id, 0.0) + amount

    balances = []
    for other_user_id, net_amount in user_balances.items():
        if abs(net_amount) > 0.01:
            other_user = db.query(User).filter(User.id == other_user_id).first()
            balances.append({
                "user_id": user_id,
                "other_user_id": other_user_id,
                "other_user_name": other_user.name if other_user else "Unknown",
                "amount": round(net_amount, 2),
                "description": f"You are owed ₹{net_amount:.2f}" if net_amount > 0 else f"You owe ₹{-net_amount:.2f}"
            })
    
    return balances


@router.get("/groups/{group_id}/balances")
def get_group_balances(group_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get balance summary for a specific group"""
    
    # Check if group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all group members (active and inactive)
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    member_ids = [m.user_id for m in members]
    
    simplified = build_raw_debts(db, group_id=group_id)
    member_balances = {}

    for (from_user_id, to_user_id), amount in simplified.items():
        if from_user_id not in member_balances:
            member_balances[from_user_id] = {}
        if to_user_id not in member_balances:
            member_balances[to_user_id] = {}

        member_balances[from_user_id][to_user_id] = member_balances[from_user_id].get(to_user_id, 0.0) - amount
        member_balances[to_user_id][from_user_id] = member_balances[to_user_id].get(from_user_id, 0.0) + amount
    
    # Convert to user-friendly format
    balances = []
    for member_id in member_ids:
        member = db.query(User).filter(User.id == member_id).first()
        if member_id in member_balances:
            for other_user_id, amount in member_balances[member_id].items():
                if abs(amount) > 0.01:
                    other_user = db.query(User).filter(User.id == other_user_id).first()
                    balances.append({
                        "user_id": member_id,
                        "user_name": member.name,
                        "other_user_id": other_user_id,
                        "other_user_name": other_user.name if other_user else "Unknown",
                        "amount": round(amount, 2),
                        "description": f"{member.name} is owed ₹{amount:.2f} by {other_user.name if other_user else 'Unknown'}" if amount > 0 else f"{member.name} owes ₹{-amount:.2f} to {other_user.name if other_user else 'Unknown'}"
                    })
    
    return balances


@router.get("/settlements")
def get_settlements_list(group_id: int = None, db: Session = Depends(get_db)):
    """
    Get simplified settlement list showing who should pay whom.
    If group_id provided, return settlements for that group only.
    """
    simplified = build_raw_debts(db, group_id=group_id)
    result = []

    for (from_user_id, to_user_id), amount in simplified.items():
        from_user = db.query(User).filter(User.id == from_user_id).first()
        to_user = db.query(User).filter(User.id == to_user_id).first()
        result.append({
            "from_user_id": from_user_id,
            "from_user_name": from_user.name if from_user else "Unknown",
            "to_user_id": to_user_id,
            "to_user_name": to_user.name if to_user else "Unknown",
            "amount": round(amount, 2),
            "description": f"{from_user.name if from_user else 'Unknown'} should pay {to_user.name if to_user else 'Unknown'} ₹{amount:.2f}",
        })

    return result


@router.post("/settlements")
def record_settlement(settlement: SettlementCreate, user_id: int, db: Session = Depends(get_db)):
    """Record a payment/settlement between two users"""
    
    # Validate users exist
    from_user = db.query(User).filter(User.id == settlement.from_user_id).first()
    to_user = db.query(User).filter(User.id == settlement.to_user_id).first()
    
    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="One or both users not found")
    
    # Create settlement record
    db_settlement = Settlement(
        from_user_id=settlement.from_user_id,
        to_user_id=settlement.to_user_id,
        group_id=settlement.group_id,
        amount=settlement.amount
    )
    db.add(db_settlement)
    db.commit()
    db.refresh(db_settlement)
    
    return SettlementResponse.from_orm(db_settlement)
