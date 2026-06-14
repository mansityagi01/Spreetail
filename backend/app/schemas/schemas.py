from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_temporary: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Group Schemas
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupResponse(GroupBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    members: List['GroupMemberResponse'] = []
    expenses: List['ExpenseResponse'] = []


# GroupMember Schemas
class GroupMemberBase(BaseModel):
    group_id: int
    user_id: int


class GroupMemberCreate(GroupMemberBase):
    pass


class GroupMemberResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    is_active: bool
    joined_at: datetime
    left_at: Optional[datetime] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# ExpenseSplit Schemas
class ExpenseSplitBase(BaseModel):
    user_id: int
    split_type: str  # "equal", "unequal", "percentage", "shares"
    split_value: float


class ExpenseSplitCreate(ExpenseSplitBase):
    pass


class ExpenseSplitResponse(ExpenseSplitBase):
    id: int
    expense_id: int
    amount_owed: float

    class Config:
        from_attributes = True


# Expense Schemas
class ExpenseCreate(BaseModel):
    group_id: Optional[int] = None
    payer_id: int
    amount: float
    currency: str = "INR"
    exchange_rate: float = 1.0
    original_amount: Optional[float] = None
    description: str
    expense_type: str  # "group" or "direct_2person"
    splits: List[ExpenseSplitCreate]


class ExpenseResponse(BaseModel):
    id: int
    group_id: Optional[int]
    payer_id: int
    amount: float
    currency: str
    exchange_rate: float
    original_amount: Optional[float]
    description: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    expense_type: str
    splits: List[ExpenseSplitResponse] = []

    class Config:
        from_attributes = True


# ExpenseChat Schemas
class ExpenseChatBase(BaseModel):
    message: str


class ExpenseChatCreate(ExpenseChatBase):
    pass


class ExpenseChatResponse(ExpenseChatBase):
    id: int
    expense_id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# Balance Schemas
class BalanceResponse(BaseModel):
    user_a_id: int
    user_b_id: int
    group_id: Optional[int]
    amount: float

    class Config:
        from_attributes = True


# Settlement Schemas
class SettlementCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float
    group_id: Optional[int] = None


class SettlementResponse(SettlementCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class DemoLoginRequest(BaseModel):
    email: str


class DemoLoginResponse(BaseModel):
    user_id: int
    email: str
    name: str
    message: str

# Import Schemas
class AnomalyResponse(BaseModel):
    row_number: int
    issue_type: str
    description: str
    action_taken: str

    class Config:
        from_attributes = True

class ImportReportResponse(BaseModel):
    filename: str
    total_rows: int
    imported_rows: int
    anomalies: List[AnomalyResponse]
