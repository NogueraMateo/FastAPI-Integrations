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

async def authenticate_user(db: Session, email: EmailStr, password: str):
    '''Checks wheather the user exits or the password given matches'''
    user: models.User = db.query(models.User).filter(models.User.email == email).first()
    if not user or not user.verify_password(password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: Optional[timedelta]= None):
    '''Generates a login access token given a dict and an expiration time'''
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
    

async def get_current_user(token: str = Depends(oauth2), db: Session= Depends(get_db)):
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