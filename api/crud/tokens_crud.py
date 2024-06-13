from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from pydantic import EmailStr
from typing import Optional
from fastapi import HTTPException
from ..config.constants import (
    CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES, EMAIL_CONFIRMATION_SECRET_KEY, ALGORITHM,
    RESET_TOKEN_EXPIRE_MINUTES, PASSWORD_RESET_SECRET_KEY
    )

class TokenServiceBase:

    def __init__(self, db: Session):
        self.db = db


    def get_token_info(self, token: str):
        pass


    def insert_token(self, user_id: int, token:str, expiry: datetime):
        pass


    async def create_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        pass


    def update_token(self, token: str, token_update: schemas.PasswordResetTokenUpdate):
        pass

    
    async def verify_token(self, token: str):
        pass



class PasswordResetTokenService(TokenServiceBase):

    def __init__(self, db: Session):
        super().__init__(db)


    def get_token_info(self, token: str) -> models.PasswordResetToken :
        return self.db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token == token).first()


    def insert_token(self, user_id: int, token:str, expiry: datetime) -> models.PasswordResetToken :
        password_reset_token = models.PasswordResetToken(
            user_id= user_id,
            token= token,
            is_used = False,
            expiry= expiry
        )
        self.db.add(password_reset_token)
        self.db.commit()
        self.db.refresh(password_reset_token)
        return password_reset_token


    async def create_token(self, data: dict, expires_delta: Optional[timedelta]= None) -> (str, datetime):
        '''Generates an access token given a dict and an expiration time'''
        to_encode = data.copy()
        if expires_delta is not None:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp' : expire})

        try:
            encoded_jwt = jwt.encode(to_encode, PASSWORD_RESET_SECRET_KEY, algorithm=ALGORITHM)
            return (encoded_jwt, expire)
        except Exception as e:
            raise Exception(f"Error encoding JWT: {str(e)}")


    def update_token(self, token: str, token_update: schemas.PasswordResetTokenUpdate) -> models.PasswordResetToken :
        token_db = self.get_token_info(token)
        if not token_db:
            raise HTTPException(status_code=404, detail="Token not found")
        update_data = token_update.model_dump()

        for key, value in update_data.items():
            setattr(token_db, key, value)

        self.db.commit()
        self.db.refresh(token_db)
        return token_db


    async def verify_token(self, token: str) -> EmailStr:
        '''Verifies whether the token generated for password reset is valid or not'''
        db_token = self.get_token_info(token)

        if db_token is not None and db_token.is_used:
            raise HTTPException(status_code=400, detail="Invalid token")
        try:
            payload = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM], audience= "password-recovery")
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
            return email
        
        except ExpiredSignatureError:
            raise expired_token_exception
        
        except JWTError:
            raise credentials_exception



class EmailConfirmationTokenService(TokenServiceBase):

    def __init__(self, db: Session):
        super().__init__(db)


    def get_token_info(self, token: str) -> models.EmailConfirmationToken :
        return self.db.query(models.EmailConfirmationToken).filter(models.EmailConfirmationToken.token == token).first()


    def insert_token(self, user_id: int, token:str, expiry: datetime) -> models.EmailConfirmationToken :
        confirm_account_token = models.EmailConfirmationToken(
            user_id= user_id,
            token= token, 
            is_used=False,
            expiry= expiry
        )
        self.db.add(confirm_account_token)
        self.db.commit()
        self.db.refresh(confirm_account_token)

        return confirm_account_token

    
    async def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> (str, datetime):

        to_encode = data.copy()
        if expires_delta is not None:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp' : expire})

        try:
            encoded_jwt = jwt.encode(to_encode, EMAIL_CONFIRMATION_SECRET_KEY, algorithm=ALGORITHM)
            return (encoded_jwt, expire)
        except Exception as e:
            raise Exception(f"Error encoding JWT: {str(e)}")


    def update_token(self, token: str, token_update: schemas.PasswordResetTokenUpdate) -> models.EmailConfirmationToken :
        token_db = self.get_token_info(token)
        if not token_db:
            raise HTTPException(status_code=404, detail="Token not found")
        update_data = token_update.model_dump()

        for key, value in update_data.items():
            setattr(token_db, key, value)

        self.db.commit()
        self.db.refresh(token_db)
        return token_db


    async def verify_token(self, token: str) -> EmailStr:
        '''Verifies whether the token generated for confirming the account is valid or not'''
        db_token = self.get_token_info(token)

        if db_token is not None and db_token.is_used:
            raise HTTPException(status_code=400, detail="Invalid token")
        try:
            payload = jwt.decode(token, EMAIL_CONFIRMATION_SECRET_KEY, algorithms=[ALGORITHM], audience= "email-confirmation")
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
            return email
        
        except ExpiredSignatureError:
            raise expired_token_exception
        
        except JWTError:
            raise credentials_exception
