from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Group, GroupMember, User
from app.schemas.schemas import GroupCreate, GroupResponse, GroupMemberResponse

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.post("/")
def create_group(group: GroupCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new group. user_id comes from auth context."""
    db_group = Group(
        name=group.name,
        description=group.description,
        created_by=user_id
    )
    db.add(db_group)
    db.flush()
    
    # Add creator as the first member
    member = GroupMember(group_id=db_group.id, user_id=user_id, is_active=True)
    db.add(member)
    db.commit()
    db.refresh(db_group)
    
    return GroupResponse.from_orm(db_group)


@router.get("/")
def list_groups(user_id: int, db: Session = Depends(get_db)):
    """List groups that the user is a member of (active or inactive)"""
    memberships = db.query(GroupMember).filter(GroupMember.user_id == user_id).all()
    groups = [m.group for m in memberships]
    return [GroupResponse.from_orm(g) for g in groups]


@router.get("/{group_id}")
def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get group details including members and expenses"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_by": group.created_by,
        "created_at": group.created_at,
        "members": [GroupMemberResponse.from_orm(m) for m in group.members],
        "expenses": [
            {
                "id": e.id,
                "description": e.description,
                "amount": e.amount,
                "payer_id": e.payer_id,
            }
            for e in group.expenses
            if not e.is_deleted
        ],
        "member_count": len(group.members),
    }


@router.post("/{group_id}/members")
def add_member(group_id: int, user_id: int, new_user_id: int, db: Session = Depends(get_db)):
    """Add a member to a group. user_id is the requester (must be a member)."""
    # Check if group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if requester is a member
    requester_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    if not requester_member:
        raise HTTPException(status_code=403, detail="You are not a member of this group")
    
    # Check if new user exists
    new_user = db.query(User).filter(User.id == new_user_id).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == new_user_id
    ).first()
    if existing:
        # Reactivate if was removed
        existing.is_active = True
        db.commit()
        return GroupMemberResponse.from_orm(existing)
    
    # Add new member
    member = GroupMember(group_id=group_id, user_id=new_user_id, is_active=True)
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return GroupMemberResponse.from_orm(member)


@router.delete("/{group_id}/members/{member_user_id}")
def remove_member(group_id: int, member_user_id: int, user_id: int, db: Session = Depends(get_db)):
    """Remove a member from a group (soft delete, keeps read-only access)."""
    # Check if group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if member exists
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == member_user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in this group")
    
    # Mark as inactive (soft delete)
    member.is_active = False
    db.commit()
    
    return {"message": "Member removed from group (read-only access retained)"}
