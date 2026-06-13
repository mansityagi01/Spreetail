from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Expense, ExpenseSplit, User, Group, ExpenseTypeEnum, ExpenseChat, ExpenseAttachment
from app.schemas.schemas import ExpenseCreate, ExpenseResponse, ExpenseChatCreate, ExpenseChatResponse
from app.services.balance_service import calculate_split_amounts


router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.post("/")
def create_expense(expense: ExpenseCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new expense with splits"""
    
    # Validate payer exists
    payer = db.query(User).filter(User.id == expense.payer_id).first()
    if not payer:
        raise HTTPException(status_code=404, detail="Payer not found")
    
    # Validate group exists (if group expense)
    if expense.expense_type == "group" and expense.group_id:
        group = db.query(Group).filter(Group.id == expense.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
    
    # Validate all split users exist
    split_user_ids = [s.user_id for s in expense.splits]
    split_users = db.query(User).filter(User.id.in_(split_user_ids)).all()
    if len(split_users) != len(split_user_ids):
        raise HTTPException(status_code=404, detail="One or more split users not found")
    
    # Calculate split amounts
    split_dict = [{"user_id": s.user_id, "split_value": s.split_value} for s in expense.splits]
    try:
        amount_owed_dict = calculate_split_amounts(
            expense.amount,
            expense.splits[0].split_type if expense.splits else "equal",
            split_dict
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create expense
    db_expense = Expense(
        group_id=expense.group_id,
        payer_id=expense.payer_id,
        amount=expense.amount,
        description=expense.description,
        created_by=user_id,
        expense_type=expense.expense_type
    )
    db.add(db_expense)
    db.flush()
    
    # Create splits
    for split in expense.splits:
        db_split = ExpenseSplit(
            expense_id=db_expense.id,
            user_id=split.user_id,
            split_type=split.split_type,
            split_value=split.split_value,
            amount_owed=amount_owed_dict[split.user_id]
        )
        db.add(db_split)
    
    db.commit()
    db.refresh(db_expense)
    
    return ExpenseResponse.from_orm(db_expense)


@router.get("/{expense_id}")
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get expense details with splits"""
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.is_deleted == False).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return ExpenseResponse.from_orm(expense)


@router.patch("/{expense_id}")
def update_expense(expense_id: int, expense_update: ExpenseCreate, user_id: int, db: Session = Depends(get_db)):
    """Update an expense (creator only)"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the creator can edit this expense")
    
    # Update expense fields
    expense.amount = expense_update.amount
    expense.description = expense_update.description
    
    # Delete old splits and create new ones
    db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
    
    # Recalculate split amounts
    split_dict = [{"user_id": s.user_id, "split_value": s.split_value} for s in expense_update.splits]
    try:
        amount_owed_dict = calculate_split_amounts(
            expense_update.amount,
            expense_update.splits[0].split_type if expense_update.splits else "equal",
            split_dict
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create new splits
    for split in expense_update.splits:
        db_split = ExpenseSplit(
            expense_id=expense.id,
            user_id=split.user_id,
            split_type=split.split_type,
            split_value=split.split_value,
            amount_owed=amount_owed_dict[split.user_id]
        )
        db.add(db_split)
    
    db.commit()
    db.refresh(expense)
    
    return ExpenseResponse.from_orm(expense)


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, user_id: int, db: Session = Depends(get_db)):
    """Delete an expense (soft delete, creator only)"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the creator can delete this expense")
    
    expense.is_deleted = True
    db.commit()
    
    return {"message": "Expense deleted"}


@router.get("/{expense_id}/chat")
def get_expense_chat(expense_id: int, db: Session = Depends(get_db)):
    """Get all chat messages for an expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    chats = db.query(ExpenseChat).filter(ExpenseChat.expense_id == expense_id).order_by(ExpenseChat.created_at).all()
    return [ExpenseChatResponse.from_orm(c) for c in chats]


@router.post("/{expense_id}/chat")
def post_expense_chat(expense_id: int, chat: ExpenseChatCreate, user_id: int, db: Session = Depends(get_db)):
    """Post a chat message on an expense (triggers WebSocket updates)"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db_chat = ExpenseChat(
        expense_id=expense_id,
        user_id=user_id,
        message=chat.message
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    
    # TODO: Emit WebSocket event here for real-time updates
    
    return ExpenseChatResponse.from_orm(db_chat)


@router.post("/{expense_id}/attachments")
async def upload_attachment(expense_id: int, file: UploadFile = File(...), user_id: int = 0, db: Session = Depends(get_db)):
    """Upload a file attachment to an expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.is_deleted == False).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Limit file size to 5MB
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")
    
    attachment = ExpenseAttachment(
        expense_id=expense_id,
        file_name=file.filename,
        file_data=contents
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {"id": attachment.id, "file_name": attachment.file_name, "uploaded_at": str(attachment.uploaded_at)}


@router.get("/{expense_id}/attachments")
def list_attachments(expense_id: int, db: Session = Depends(get_db)):
    """List all attachments for an expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return [
        {"id": a.id, "file_name": a.file_name, "uploaded_at": str(a.uploaded_at)}
        for a in expense.attachments
    ]


@router.get("/attachments/{attachment_id}/download")
def download_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Download a specific attachment"""
    attachment = db.query(ExpenseAttachment).filter(ExpenseAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return Response(
        content=attachment.file_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{attachment.file_name}"'}
    )
