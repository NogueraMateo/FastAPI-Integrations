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
from ..config.exceptions import credentials_exception, expired_token_exception


class TokenServiceBase:

    def __init__(self, db: Session):
        self.db = db


    def get_token_info(self, token: str):
        pass


    def insert_token(self, user_id: int, token:str, expiry: datetime):
        pass


    async def create_token(self, data: dict, expires_delta: Optional[timedelta] = None, secret_key: str = None):
        pass


    def update_token(self, token: str, token_update: schemas.PasswordResetTokenUpdate):
        pass

    
    async def verify_token(self, token: str):
        pass



class PasswordResetTokenService(TokenServiceBase):
    """
    A service class for managing password reset tokens.

    Attributes:
        db (Session): The database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the PasswordResetTokenService with the provided database session.

        Args:
            db (Session): The database session.
        """
        super().__init__(db)


    def get_token_info(self, token: str) -> models.PasswordResetToken :
        """
        Retrieve information about a specific password reset token.

        Args:
            token (str): The password reset token.

        Returns:
            models.PasswordResetToken: The password reset token information.
        """
        return self.db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token == token).first()


    def insert_token(self, user_id: int, token:str, expiry: datetime) -> models.PasswordResetToken:
        """
        Insert a new password reset token into the database.

        Args:
            user_id (int): The ID of the user requesting the password reset.
            token (str): The password reset token.
            expiry (datetime): The expiration date and time of the token.

        Returns:
            models.PasswordResetToken: The newly created password reset token.
        """
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


    async def create_token(self, data: dict, expires_delta: Optional[timedelta]= None, secret_key: str = None) -> (str, datetime):
        """
        Generate a token for password reset.

        Args:
            data (dict): The data to encode into the token.
            expires_delta (Optional[timedelta]): The expiration time delta for the token.

        Returns:
            tuple: A tuple containing the encoded JWT token and its expiration time.
        """
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
        """
        Update an existing password reset token.

        Args:
            token (str): The token to update.
            token_update (schemas.PasswordResetTokenUpdate): The updated token data.

        Returns:
            models.PasswordResetToken: The updated password reset token.
        """

        token_db = self.get_token_info(token)
        if not token_db:
            raise HTTPException(status_code=404, detail="Token not found")
        update_data = token_update.model_dump()

        for key, value in update_data.items():
            setattr(token_db, key, value)

        self.db.commit()
        self.db.refresh(token_db)
        return token_db


    async def verify_token(self, token: str) -> (EmailStr, int):
        """
        Verify the validity of a password reset token.

        Args:
            token (str): The token to verify.

        Returns:
            EmailStr: The email address associated with the valid token.

        Raises:
            HTTPException: If the token is invalid or expired.
        """

        db_token = self.get_token_info(token)

        if db_token is not None and db_token.is_used:
            raise HTTPException(status_code=400, detail="Invalid token")
        try:
            payload = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM], audience= "password-recovery")
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
            user_id = payload.get("id")
            return (email, user_id)
        
        except ExpiredSignatureError:
            raise expired_token_exception
        
        except JWTError:
            raise credentials_exception



class EmailConfirmationTokenService(TokenServiceBase):
    """
    A service class for managing email confirmation tokens.

    Attributes:
        db (Session): The database session.
    """
    
    def __init__(self, db: Session):
        """
        Retrieve information about a specific email confirmation token.

        Args:
            token (str): The email confirmation token.

        Returns:
            models.EmailConfirmationToken: The email confirmation token information.
        """
        super().__init__(db)


    def get_token_info(self, token: str) -> models.EmailConfirmationToken :
        """
        Insert a new email confirmation token into the database.

        Args:
            user_id (int): The ID of the user requesting email confirmation.
            token (str): The email confirmation token.
            expiry (datetime): The expiration date and time of the token.

        Returns:
            models.EmailConfirmationToken: The newly created email confirmation token.
        """
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

    
    async def create_token(self, data: dict, expires_delta: Optional[timedelta] = None, secret_key: str = None) -> (str, datetime):
        """
        Generate an email confirmation token.

        Args:
            data (dict): The data to encode into the token.
            expires_delta (Optional[timedelta]): The expiration time delta for the token.

        Returns:
            tuple: A tuple containing the encoded JWT token and its expiration time.
        """

        to_encode = data.copy()
        if expires_delta is not None:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp' : expire})

        try:
            encoded_jwt = jwt.encode(to_encode, EMAIL_CONFIRMATION_SECRET_KEY if secret_key is None else secret_key, algorithm=ALGORITHM)
            return (encoded_jwt, expire)
        except Exception as e:
            raise Exception(f"Error encoding JWT: {str(e)}")


    def update_token(self, token: str, token_update: schemas.PasswordResetTokenUpdate) -> models.EmailConfirmationToken :
        """
        Update an existing email confirmation token.

        Args:
            token (str): The token to update.
            token_update (schemas.PasswordResetTokenUpdate): The updated token data.

        Returns:
            models.EmailConfirmationToken: The updated email confirmation token.
        """
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
        """
        Verify the validity of an email confirmation token.

        Args:
            token (str): The token to verify.

        Returns:
            EmailStr: The email address associated with the valid token.

        Raises:
            HTTPException: If the token is invalid or expired.
        """
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
