from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

# --------------------------- USER SCHEMAS ---------------------------
class UserBase(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    lastname: str
    email: EmailStr
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True

# Creating an user
class UserCreate(UserBase):
    document: Optional[str] = None
    plain_password: Optional[str] = None
    google_access_token: Optional[str] = None

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
    
    @field_validator('phone_number')
    def phone_number_must_not_be_empty(cls, v):
        if not v:  # Esto verificará tanto None como strings vacíos
            raise ValueError('Phone number field must be provided')
        return v

    @field_validator('document')
    def document_must_not_be_empty(cls, v):
        if not v:  # Esto verificará tanto None como strings vacíos
            raise ValueError('Document field must be provided')
        return v


class UserCreateByAdmin(UserCreate):
    role: Optional[str]

    
# Schema expected when updating an user
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    plain_password: Optional[str] = None
    phone_number: Optional[str] = None
    last_meeting_scheduled: Optional[datetime]= None
    is_active: Optional[bool] = None    
    role: Optional[str] = None
    google_access_token: Optional[str] = None

    class Config:
        from_attributes= True


# --------------------------- PASSWORD RESET TOKENS SCHEMAS ---------------------------

class PasswordResetTokenBase(BaseModel):
    token: str
    expiry: datetime

    class Config:
        from_attributes = True

class PasswordResetTokenCreate(PasswordResetTokenBase):
    is_used: bool
    user_id: int

class PasswordResetTokenUpdate(BaseModel):
    is_used: bool

class PasswordResetToken(PasswordResetTokenBase):
    id: int
    is_used: bool
    user: 'UserBase'

    class Config:
        from_attributes = True

# --------------------------- EMAIL TOKENS SCHEMAS ---------------------------
class EmailConfirmationTokenBase(BaseModel):
    token: str
    expiry: datetime

    class Config:
        from_attributes = True

class EmailConfirmationTokenCreate(EmailConfirmationTokenBase):
    is_used: bool
    user_id: int

class EmailConfirmationTokenUpdate(BaseModel):
    is_used: bool

class EmailConfirmationToken(EmailConfirmationTokenBase):
    id: int
    is_used: bool
    user: 'UserBase'

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: EmailStr


# Base model for advisors
class AdvisorBase(BaseModel):
    name: str
    email: EmailStr

class AdvisorCreate(AdvisorBase):
    pass

class Advisor(AdvisorBase):
    id: int
    meetings: List['Meeting'] = []  # List of associated meetings

    class Config:
        from_attributes = True

# Base model for meetings
class MeetingBase(BaseModel):
    start_time: datetime
    zoom_meeting_id: Optional[str] = None
    join_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class MeetingCreate(BaseModel):
    start_time: datetime
    topic: str

class MeetingUpdate(BaseModel):
    start_time: datetime

class Meeting(MeetingBase):
    id: int
    user_id:int
    advisor_id: int
    topic: str

    class Config:
        from_attributes = True

    
# Reading an user
class User(UserBase):
    id: int
    is_active: bool
    role: str
    google_access_token: Optional[str] = None
    meetings: List[Meeting] = []
    reset_tokens: List[PasswordResetToken] = []
    email_confirmation_tokens: List[EmailConfirmationToken] = []


class TokenData(BaseModel):
    email: EmailStr | None = None

class ResetPasswordFields(BaseModel):
    token: str
    new_password:str
    new_password_confirm:str


User.model_rebuild()
PasswordResetToken.model_rebuild()
EmailConfirmationToken.model_rebuild()
Advisor.model_rebuild()
