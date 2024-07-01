from fastapi import Depends, HTTPException
from fastapi.security.base import SecurityBase
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi import Request
from jose import JWTError, jwt, ExpiredSignatureError
from .. import models
from ..config.constants import ACCESS_TOKEN_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from ..config.exceptions import credentials_exception, expired_token_exception
from sqlalchemy.orm import Session
from ..database import get_db


class OAuth2PasswordBearerWithCookie(SecurityBase):
    def __init__(self, *, auto_error: bool = True):
        self.model = APIKey(
            **{"name": "access_token", "in": APIKeyIn.cookie}
        )
        self.scheme_name = self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            if self.auto_error:
                raise credentials_exception
            else:
                return None
        return token

oauth2_scheme = OAuth2PasswordBearerWithCookie()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session= Depends(get_db)) -> models.User:
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