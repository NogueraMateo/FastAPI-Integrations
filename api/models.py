from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from .database import Base
import enum

crypt = CryptContext(schemes=["bcrypt"])

class UserRole(enum.Enum):
    REGULAR = "REGULAR"
    ADMIN = "ADMIN"

class User(Base):
    """
    Represents a user in the application.

    Attributes:
        id (int): The primary key of the user.
        first_name (str): The first name of the user.
        second_name (str): The second name of the user.
        lastname (str): The last name of the user.
        email (str): The unique email address of the user.
        phone_number (str): The unique phone number of the user.
        password_hash (str): The hashed password of the user.
        document (str): The unique document identifier of the user.
        date_of_creation (datetime): The timestamp when the user was created.
        last_meeting_scheduled (datetime): The timestamp of the last meeting scheduled by the user.
        is_active (bool): Indicates whether the user's account is active.
        role (str): The role of the user (e.g., "REGULAR", "ADMIN").
        google_access_token (str): The Google access token for the user.
        meetings (list[Meeting]): The meetings associated with the user.
        reset_tokens (list[PasswordResetToken]): The password reset tokens associated with the user.
        email_confirmation_tokens (list[EmailConfirmationToken]): The email confirmation tokens associated with the user.
    """

    __tablename__ = 'users'

    id= Column(Integer, primary_key= True)
    first_name= Column(String, nullable= False)
    second_name= Column(String)
    lastname= Column(String, nullable= False)
    email= Column(String, unique= True, nullable= False, index= True)
    phone_number= Column(String, unique= True, nullable=True)
    password_hash= Column(String, nullable= True)
    document= Column(String, unique= True, nullable= True)
    date_of_creation= Column(DateTime, default= lambda: datetime.now(timezone.utc))
    last_meeting_scheduled = Column(DateTime(timezone=True), default=None)
    is_active = Column(Boolean, default= False, nullable= False)
    role = Column(Enum(UserRole), default=UserRole.REGULAR, nullable=False)
    google_access_token = Column(String, nullable=True)

    meetings= relationship('Meeting', back_populates= 'user', cascade="all, delete-orphan") 
    reset_tokens= relationship('PasswordResetToken', back_populates= 'user', cascade="all, delete-orphan")
    email_confirmation_tokens = relationship('EmailConfirmationToken', back_populates='user', cascade= "all, delete-orphan")
    

    def verify_password(self, plain_password: str):
        """
        Verify the provided plain password against the stored password hash.

        Args:
            plain_password (str): The plain text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return crypt.verify(plain_password, self.password_hash)
    
    def can_schedule_meeting(self):
        """
        Check if the user can schedule a new meeting.

        Returns:
            bool: True if the user can schedule a meeting, False otherwise.
        """
        if not self.last_meeting_scheduled:
            return True

        # Se verifica si han pasado al menos 7 dias desde la última cita agendada.
        last_meeting_date = self.last_meeting_scheduled
        now = datetime.now(timezone.utc)
        if now - last_meeting_date >= timedelta(days=7):
            return True
        else:
            return False

class PasswordResetToken(Base):
    """
    Represents a password reset token for a user.

    Attributes:
        id (int): The primary key of the token.
        token (str): The unique token string.
        user_id (int): The foreign key to the user.
        is_used (bool): Indicates whether the token has been used.
        expiry (datetime): The expiry timestamp of the token.
        user (User): The user associated with the token.
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key= True)
    token= Column(String, unique=True, nullable= False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable= False)
    is_used = Column(Boolean, default= False, nullable= False)
    expiry = Column(DateTime, nullable=False)

    # Relationship with the USER
    user = relationship('User', back_populates='reset_tokens')


class EmailConfirmationToken(Base):
    """
    Represents an email confirmation token for a user.

    Attributes:
        id (int): The primary key of the token.
        token (str): The unique token string.
        user_id (int): The foreign key to the user.
        is_used (bool): Indicates whether the token has been used.
        expiry (datetime): The expiry timestamp of the token.
        user (User): The user associated with the token.
    """
    __tablename__ = "email_confirmation_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expiry = Column(DateTime, nullable=False)

    # Relationship with the User
    user = relationship('User', back_populates= 'email_confirmation_tokens')


class Meeting(Base):
    """
    Represents a meeting scheduled between a user and an advisor.

    Attributes:
        id (int): The primary key of the meeting.
        start_time (datetime): The start time of the meeting.
        topic (str): The topic of the meeting.
        zoom_meeting_id (str): The unique Zoom meeting ID.
        join_url (str): The URL to join the Zoom meeting.
        user_id (int): The foreign key to the user.
        advisor_id (int): The foreign key to the advisor.
        user (User): The user who scheduled the meeting.
        advisor (Advisor): The advisor assigned to the meeting.
    """
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    topic = Column(String)
    zoom_meeting_id = Column(String, unique=True)
    join_url = Column(String, unique=True)
    
    # Llave foránea de Advisor
    user_id = Column(Integer, ForeignKey('users.id'))
    advisor_id = Column(Integer, ForeignKey('advisors.id'))
    advisor = relationship("Advisor", back_populates="meetings")
    user = relationship("User", back_populates='meetings')


class Advisor(Base):
    """
    Represents an advisor in the application.

    Attributes:
        id (int): The primary key of the advisor.
        name (str): The name of the advisor.
        email (str): The unique email address of the advisor.
        last_assigned_time (datetime): The timestamp of the last assignment.
        meetings (list[Meeting]): The meetings associated with the advisor.
    """
    __tablename__ = 'advisors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    last_assigned_time = Column(DateTime, default= lambda: datetime.now(timezone.utc))
    
    # Relación con reuniones
    meetings = relationship("Meeting", back_populates="advisor")


