from dotenv import load_dotenv
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from pydantic import EmailStr
from typing import Optional
from .. import models, schemas
from datetime import timedelta, datetime, timezone
from ..config.constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, ACCESS_TOKEN_SECRET_KEY

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
    

