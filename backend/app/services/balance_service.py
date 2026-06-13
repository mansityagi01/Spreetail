"""
Balance calculation service
Handles splitting logic and debt simplification
"""

from typing import Dict, List, Tuple
from app.models.models import Expense, ExpenseSplit, Balance


def calculate_split_amounts(
    total_amount: float,
    split_type: str,
    splits: List[Dict]  # [{"user_id": 1, "split_value": amount_or_percentage_or_shares}, ...]
) -> Dict[int, float]:
    """
    Calculate amount owed by each participant based on split type.
    
    Args:
        total_amount: Total expense amount
        split_type: One of "equal", "unequal", "percentage", "shares"
        splits: List of split entries with user_id and split_value
    
    Returns:
        Dict mapping user_id to amount they owe
    """
    result = {}
    
    if split_type == "equal":
        # Each person owes: total / number of people
        num_people = len(splits)
        amount_per_person = total_amount / num_people
        for split in splits:
            result[split["user_id"]] = amount_per_person
    
    elif split_type == "unequal":
        # Each person owes the exact amount specified in split_value
        # Validate that sum equals total
        total_specified = sum(s["split_value"] for s in splits)
        if abs(total_specified - total_amount) > 0.01:  # Allow small rounding error
            raise ValueError(f"Unequal splits must sum to {total_amount}, got {total_specified}")
        for split in splits:
            result[split["user_id"]] = split["split_value"]
    
    elif split_type == "percentage":
        # Each person owes: (split_value / 100) * total_amount
        # Validate that percentages sum to 100
        total_percentage = sum(s["split_value"] for s in splits)
        if abs(total_percentage - 100) > 0.01:  # Allow small rounding error
            raise ValueError(f"Percentage splits must sum to 100, got {total_percentage}")
        for split in splits:
            result[split["user_id"]] = (split["split_value"] / 100) * total_amount
    
    elif split_type == "shares":
        # Each person owes: (split_value / total_shares) * total_amount
        total_shares = sum(s["split_value"] for s in splits)
        share_value = total_amount / total_shares
        for split in splits:
            result[split["user_id"]] = split["split_value"] * share_value
    
    else:
        raise ValueError(f"Unknown split type: {split_type}")
    
    return result


def simplify_debts(balances: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], float]:
    """
    Simplify debts by netting off reciprocal debts.
    
    Args:
        balances: Dict mapping (from_user_id, to_user_id) to amount owed
    
    Returns:
        Simplified balances dict
    """
    # Create a dict of net balances for each user pair
    net_balances = {}
    
    for (user_a, user_b), amount in balances.items():
        key = (min(user_a, user_b), max(user_a, user_b))
        
        if key not in net_balances:
            net_balances[key] = {}
        
        if user_a < user_b:
            # A owes B
            net_balances[key]["A_to_B"] = net_balances[key].get("A_to_B", 0) + amount
        else:
            # B owes A
            net_balances[key]["B_to_A"] = net_balances[key].get("B_to_A", 0) + amount
    
    # Net off reciprocal debts
    simplified = {}
    for (user_a, user_b), debts in net_balances.items():
        a_to_b = debts.get("A_to_B", 0)
        b_to_a = debts.get("B_to_A", 0)
        net = a_to_b - b_to_a
        
        if net > 0.01:  # Allow small rounding error
            simplified[(user_a, user_b)] = net  # A owes B
        elif net < -0.01:
            simplified[(user_b, user_a)] = -net  # B owes A
        # If net is ~0, no balance
    
    return simplified


def calculate_user_balance_in_group(
    user_id: int,
    group_id: int,
    expenses: List[Expense],
    db=None
) -> float:
    """
    Calculate net balance for a user in a specific group.
    Positive = user is owed money. Negative = user owes money.
    """
    balance = 0.0
    
    for expense in expenses:
        if expense.is_deleted:
            continue
        if expense.group_id != group_id:
            continue
        
        # If user is the payer, they are owed back
        if expense.payer_id == user_id:
            balance += expense.amount
        
        # Find this user in the splits and subtract what they owe
        for split in expense.splits:
            if split.user_id == user_id:
                balance -= split.amount_owed
    
    return balance


def get_settlement_list(balances: Dict[int, float]) -> List[Dict]:
    """
    Convert user balances to a settlement list showing who should pay whom.
    
    Args:
        balances: Dict mapping user_id to net balance (positive = owed, negative = owes)
    
    Returns:
        List of {from_user_id, to_user_id, amount} representing who pays whom
    """
    settlements = []
    
    # Sort users into debtors (negative balance) and creditors (positive balance)
    debtors = [(uid, -bal) for uid, bal in balances.items() if bal < -0.01]
    creditors = [(uid, bal) for uid, bal in balances.items() if bal > 0.01]
    
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    # Match debtors with creditors
    for debtor_uid, debtor_amount in debtors:
        for creditor_uid, creditor_amount in creditors:
            if creditor_amount < 0.01:
                break
            
            settlement_amount = min(debtor_amount, creditor_amount)
            settlements.append({
                "from_user_id": debtor_uid,
                "to_user_id": creditor_uid,
                "amount": settlement_amount
            })
            
            debtor_amount -= settlement_amount
            creditors_idx = creditors.index((creditor_uid, creditor_amount))
            creditors[creditors_idx] = (creditor_uid, creditor_amount - settlement_amount)
    
    return settlements
