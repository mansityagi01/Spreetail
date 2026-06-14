from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import DemoLoginRequest, DemoLoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Demo users - seeded data
DEMO_USERS = [
    {"email": "mansi@splitwise.app", "name": "Mansi"},
    {"email": "hari@splitwise.app", "name": "Hari"},
    {"email": "aisha@splitwise.app", "name": "Aisha"},
    {"email": "rohan@splitwise.app", "name": "Rohan"},
    {"email": "priya@splitwise.app", "name": "Priya"},
    {"email": "meera@splitwise.app", "name": "Meera"},
    {"email": "dev@splitwise.app", "name": "Dev"},
    {"email": "sam@splitwise.app", "name": "Sam"},
]


def seed_demo_users(db: Session):
    """Seed demo users into the database if they don't exist"""
    for demo_user in DEMO_USERS:
        existing = db.query(User).filter(User.email == demo_user["email"]).first()
        if not existing:
            user = User(email=demo_user["email"], name=demo_user["name"])
            db.add(user)
    db.commit()


@router.post("/demo-login")
def demo_login(request: DemoLoginRequest, db: Session = Depends(get_db)):
    """
    Demo login endpoint. Returns a demo user if they exist.
    In production, this would be replaced with OAuth or proper auth.
    """
    # Seed users on first login
    seed_demo_users(db)
    
    # Check if email is a valid demo user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid demo user")
    
    return DemoLoginResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        message="Demo login successful"
    )


@router.get("/demo-users")
def get_demo_users():
    """
    Return list of available demo users for the frontend.
    Helps users know which emails to use for login.
    """
    return {
        "demo_users": DEMO_USERS,
        "message": "Use any of these emails to demo login"
    }
