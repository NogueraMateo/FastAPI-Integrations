from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from .database import Base

crypt = CryptContext(schemes=["bcrypt"])

class User(Base):
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
    role = Column(String, default="REGULAR", nullable=False)

    meetings= relationship('Meeting', back_populates= 'user', cascade="all, delete-orphan") 
    reset_tokens= relationship('PasswordResetToken', back_populates= 'user', cascade="all, delete-orphan")
    email_confirmation_tokens = relationship('EmailConfirmationToken', back_populates='user', cascade= "all, delete-orphan")
    

    def verify_password(self, plain_password: str):
        return crypt.verify(plain_password, self.password_hash)
    
    def can_schedule_meeting(self):
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
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key= True)
    token= Column(String, unique=True, nullable= False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable= False)
    is_used = Column(Boolean, default= False, nullable= False)
    expiry = Column(DateTime, nullable=False)

    # Relationship with the USER
    user = relationship('User', back_populates='reset_tokens')


class EmailConfirmationToken(Base):
    __tablename__ = "email_confirmation_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expiry = Column(DateTime, nullable=False)

    # Relationship with the User
    user = relationship('User', back_populates= 'email_confirmation_tokens')


class Meeting(Base):
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
    __tablename__ = 'advisors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    last_assigned_time = Column(DateTime, default= lambda: datetime.now(timezone.utc))
    
    # Relación con reuniones
    meetings = relationship("Meeting", back_populates="advisor")


