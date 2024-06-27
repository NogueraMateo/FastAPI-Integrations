from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional, List
from datetime import datetime

class CustomBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes = True, extra = 'forbid')

# --------------------------- USER SCHEMAS ---------------------------
class UserBase(CustomBaseModel):
    first_name: str
    second_name: Optional[str] = None
    lastname: str
    email: EmailStr
    phone_number: Optional[PhoneNumber] = None

# Creating an user
class UserCreate(UserBase):
    document: Optional[str] = None
    plain_password: str

    @field_validator('first_name')
    def first_name_must_not_be_empty(cls, v):
        if not v:  # Esto verificará tanto None como strings vacíos
            raise ValueError('First name field must be provided')
        return v
    
    @field_validator('lastname')
    def second_name_must_not_be_empty(cls, v):
        if not v:  # Esto verificará tanto None como strings vacíos
            raise ValueError('Lastname field must be provided')
        return v

class UserCreateGoogle(UserBase):
    document: Optional[str] = None
    plain_password: Optional[str] = None
    google_access_token: Optional[str] = None

class UserCreateByAdmin(UserCreate):
    role: Optional[str]

    
# Schema expected when updating an user
class UserUpdate(CustomBaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    plain_password: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    last_meeting_scheduled: Optional[datetime]= None
    is_active: Optional[bool] = None    
    role: Optional[str] = None
    google_access_token: Optional[str] = None


# --------------------------- PASSWORD RESET TOKENS SCHEMAS ---------------------------

class PasswordResetTokenBase(CustomBaseModel):
    token: str
    expiry: datetime


class PasswordResetTokenCreate(PasswordResetTokenBase):
    is_used: bool
    user_id: int

class PasswordResetTokenUpdate(CustomBaseModel):
    is_used: bool

class PasswordResetToken(PasswordResetTokenBase):
    id: int
    is_used: bool
    user: 'UserBase'

# --------------------------- EMAIL TOKENS SCHEMAS ---------------------------
class EmailConfirmationTokenBase(CustomBaseModel):
    token: str
    expiry: datetime



class EmailConfirmationTokenCreate(EmailConfirmationTokenBase):
    is_used: bool
    user_id: int

class EmailConfirmationTokenUpdate(CustomBaseModel):
    is_used: bool

class EmailConfirmationToken(EmailConfirmationTokenBase):
    id: int
    is_used: bool
    user: 'UserBase'


class TokenData(CustomBaseModel):
    email: EmailStr


# Base model for advisors
class AdvisorBase(CustomBaseModel):
    name: str
    email: EmailStr

class AdvisorCreate(AdvisorBase):
    pass

class Advisor(AdvisorBase):
    id: int
    meetings: List['Meeting'] = []  # List of associated meetings


class MeetingBase(CustomBaseModel):
    start_time: datetime
    zoom_meeting_id: Optional[str] = None
    join_url: Optional[str] = None

class MeetingCreate(CustomBaseModel):
    start_time: datetime
    topic: str

class MeetingUpdate(CustomBaseModel):
    start_time: datetime

class Meeting(MeetingBase):
    id: int
    user_id:int
    advisor_id: int
    topic: str

    
# Reading an user
class User(UserBase):
    id: int
    is_active: bool
    role: str
    google_access_token: Optional[str] = None
    meetings: List[Meeting] = []
    reset_tokens: List[PasswordResetToken] = []
    email_confirmation_tokens: List[EmailConfirmationToken] = []


class TokenData(CustomBaseModel):
    email: EmailStr | None = None

class ResetPasswordFields(CustomBaseModel):
    token: str
    new_password:str
    new_password_confirm:str


class ConfirmBase(CustomBaseModel):
    token: str

User.model_rebuild()
PasswordResetToken.model_rebuild()
EmailConfirmationToken.model_rebuild()
Advisor.model_rebuild()
