from .auth import redis_client
from ..services.user_service import UserService
from ..services.token_service import PasswordResetTokenService
from ..services.email_service import EmailService

from ..schemas import UserUpdate, PasswordResetTokenUpdate, ResetPasswordFields
from ..database import get_db

from ..utils.rate_limiting import rate_limit_exceeded
from ..config.constants import PASSWORD_RATE_LIMIT_PERIOD
from fastapi import APIRouter, HTTPException, Depends, Form, Request
from sqlalchemy.orm import Session


router= APIRouter(tags=["Password Recovery"])


@router.get("/password-recovery/{email}")
async def password_recovery(email: str, request: Request, db: Session = Depends(get_db)):
    """
    Initiate a password recovery process by sending a reset password link to the user's email.

    Args:
        email (str): The email address of the user requesting password recovery.
        background_tasks (BackgroundTasks): FastAPI background tasks for sending the email asynchronously.
        request (Request): The HTTP request object to extract the client's IP address for rate limiting.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message confirming that the password reset link has been sent, and the generated token.

    Raises:
        HTTPException: If the rate limit is exceeded (status code 429).
        HTTPException: If the user does not exist (status code 404).
    """
    # Services
    user_service = UserService(db)
    token_service = PasswordResetTokenService(db)
    email_service = EmailService()

    # Client IP as identifier for rate limiting
    client_ip = request.client.host
    identifier = f"{client_ip}:{email}"
    
    # Rate limiting: 5 requests per hour
    if rate_limit_exceeded(redis_client, identifier, max_requests=5, period=PASSWORD_RATE_LIMIT_PERIOD):
        raise HTTPException(status_code=429, detail= "Rate limit exceeded, please try again later.")

    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="The user doesn't exist.")
    
    # Generate token with useful information and expiration time
    token_data = {"sub": email, "id": user.id, "aud": "password-recovery"}
    password_reset_token, expiry = await token_service.create_token(
        data= token_data
    )
    
    token_service.insert_token(user_id=user.id, token= password_reset_token, expiry= expiry)
    await email_service.send_reset_password_email(email, password_reset_token)

    return {"msg": "The link to reset your password has been sent, please check your email."}


@router.patch("/reset-password")
async def reset_password(info: ResetPasswordFields, db: Session = Depends(get_db)):
    """
    Reset the user's password using the provided token and new password.

    Args:
        info (ResetPasswordFields): The fields required for resetting the password, including the token, new password, and password confirmation.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message confirming that the password has been updated successfully.

    Raises:
        HTTPException: If the token is invalid or expired.
        HTTPException: If the user is not found (status code 404).
        HTTPException: If the passwords do not match (status code 400).
        HTTPException: If the password is less than 7 characters long (status code 400).
    """
    token_service = PasswordResetTokenService(db)
    user_service = UserService(db)

    email, user_id = await token_service.verify_token(info.token)
    
    if info.new_password != info.new_password_confirm:
        token_update= PasswordResetTokenUpdate(is_used= True)
        token_service.update_token(token= info.token, token_update=token_update)
        raise HTTPException(status_code= 400, detail= "Passwords don't match.")

    if len(info.new_password) < 7:
        token_update= PasswordResetTokenUpdate(is_used= True)
        token_service.update_token(token= info.token, token_update=token_update)
        raise HTTPException(status_code=400, detail="Password must be at least 7 characters long")

    user_update = UserUpdate(plain_password= info.new_password)
    user_service.update_user(user_id= user_id, user_update= user_update)

    token_update= PasswordResetTokenUpdate(is_used= True)
    token_service.update_token(token= info.token, token_update=token_update)

    return {"msg" : "The password has been updated succesfully"}
