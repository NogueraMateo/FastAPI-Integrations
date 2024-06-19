from dotenv import load_dotenv
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from pydantic import EmailStr
from typing import Optional
from ..config.exceptions import credentials_exception, expired_token_exception
from .. import models, schemas
from ..config.constants import ACCESS_TOKEN_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from datetime import timedelta, datetime, timezone

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

async def authenticate_user(db: Session, email: EmailStr, password: str) -> models.User | bool:
    """
    Authenticate the user by checking if the user exists and the given password matches.

    Args:
        db (Session): The database session.
        email (EmailStr): The email address of the user.
        password (str): The password provided by the user.

    Returns:
        models.User | bool: The authenticated user object or False if authentication fails.
    """
    user: models.User = db.query(models.User).filter(models.User.email == email).first()
    if not user or not user.verify_password(password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: Optional[timedelta]= None) -> str:
    """
    Generate a login access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[timedelta], optional): The expiration time of the token. Defaults to None.

    Returns:
        str: The encoded JWT token.

    Raises:
        Exception: If there is an error encoding the JWT.
    """
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp' : expire})

    try:
        encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise Exception(f"Error encoding JWT: {str(e)}")
    

def get_current_user(token: str = Depends(oauth2), db: Session= Depends(get_db)) -> models.User:
    """
    Retrieve the current authenticated user from the database using the provided JWT token.

    Args:
        token (str, optional): The JWT token provided by the user. Defaults to Depends(oauth2).
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        models.User: The authenticated user object.

    Raises:
        HTTPException: If the token is expired or invalid, or if the user is not found.
    """
    try:
        payload= jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)

    except ExpiredSignatureError:
        raise expired_token_exception
    
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Retrieve the authenticated and active user from the database

    Args:
        current_user (User) : Provided by the get_current_user function

    Returns:
        models.User: The active and authenticated user object.

    Raises:
        HTTPException: If the user is not active
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: models.User = Depends(get_current_active_user)) -> models.User:
    """
    Retrieve user if it has the ADMIN role

    Args:
        current_user (User) : Provided by the get_current_active_user function

    Returns:
        models.User: The active, authenticated and ADMIN user object.

    Raises:
        HTTPException: If the user has not ADMIN role
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted"
        )
    return current_user