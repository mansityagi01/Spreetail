from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, LargeBinary, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    groups = relationship("GroupMember", back_populates="user")
    expenses_created = relationship("Expense", foreign_keys="Expense.created_by", back_populates="creator")
    expenses_paid = relationship("Expense", foreign_keys="Expense.payer_id", back_populates="payer")
    splits = relationship("ExpenseSplit", back_populates="user")
    chats = relationship("ExpenseChat", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    is_active = Column(Boolean, default=True)  # Can be removed but retain read-only access
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="groups")


class ExpenseTypeEnum(str, enum.Enum):
    group = "group"
    direct_2person = "direct_2person"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    payer_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Float)  # In Indian Rupees
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    expense_type = Column(Enum(ExpenseTypeEnum), default=ExpenseTypeEnum.group)

    # Relationships
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", foreign_keys=[payer_id], back_populates="expenses_paid")
    creator = relationship("User", foreign_keys=[created_by], back_populates="expenses_created")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")
    attachments = relationship("ExpenseAttachment", back_populates="expense", cascade="all, delete-orphan")
    chats = relationship("ExpenseChat", back_populates="expense", cascade="all, delete-orphan")


class SplitTypeEnum(str, enum.Enum):
    equal = "equal"
    unequal = "unequal"
    percentage = "percentage"
    shares = "shares"


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    split_type = Column(Enum(SplitTypeEnum))
    split_value = Column(Float)  # Amount, percentage, or shares depending on split_type
    amount_owed = Column(Float, default=0.0)  # Calculated amount owed

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="splits")


class ExpenseAttachment(Base):
    __tablename__ = "expense_attachments"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), index=True)
    file_name = Column(String(255))
    file_data = Column(LargeBinary)  # Binary file data
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    expense = relationship("Expense", back_populates="attachments")


class ExpenseChat(Base):
    __tablename__ = "expense_chats"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    expense = relationship("Expense", back_populates="chats")
    user = relationship("User", back_populates="chats")


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"), index=True)
    user_b_id = Column(Integer, ForeignKey("users.id"), index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    amount = Column(Float, default=0.0)  # Net amount owed by user_a to user_b
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    amount = Column(Float)  # Amount paid in INR
    created_at = Column(DateTime, default=datetime.utcnow)
