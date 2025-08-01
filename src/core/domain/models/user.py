from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class User(BaseModel):
    id: int
    name: str
    birth_date: date
    gender: Gender
    # is_approved: bool
    # has_requested_access: Optional[bool] = None
    is_admin: Optional[bool] = None
    # q_ok: Optional[int] = None
    # q_tot: Optional[int] = None
    # streak: Optional[int] = None
    # last: Optional[datetime] = None
    status: Literal["pending", "approved", "rejected"] = "pending"
    telegram_id: int
    first_active: Optional[datetime] = None
    last_active: Optional[datetime] = None
    registered_at: Optional[datetime] = None


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    photo_url: Optional[str] = None


class UserBase(BaseModel):
    pass


class UserResponse(BaseModel):
    name: str
    birth_date: date
    gender: Gender
    stars: int = 0
    total_questions: int = 0
    card_count: int = 0
    is_admin: bool = False
    avatar: Optional[str] = None
    status: Literal["pending", "approved", "rejected"] = "pending"
    telegram_id: int
    first_active: Optional[datetime] = None
    last_active: Optional[datetime] = None
    registered_at: Optional[datetime] = None


class UserProfileResponse(BaseModel):
    success: bool
    data: UserResponse


class ModerationRequest(BaseModel):
    user_id: int
    action: Literal["approve", "reject"]
    admin_id: int


class TelegramWebhook(BaseModel):
    callback_query: Optional[dict] = None
    message: Optional[dict] = None
