from .auth import redis_client

from ..crud.user_crud import UserService
from ..crud.tokens_crud import PasswordResetTokenService

from ..schemas import UserUpdate, PasswordResetTokenUpdate, ResetPasswordFields
from ..database import get_db
from ..utils.password_reset_utils import send_reset_password_email

from ..utils.rate_limiting import rate_limit_exceeded

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Form, Request
from sqlalchemy.orm import Session


router= APIRouter()


@router.get("/password-recovery/{email}")
async def password_recovery(email: str, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):

    # Servicios necesarios
    user_service = UserService(db)
    token_service = PasswordResetTokenService(db)

    # Usando la IP del cliente como identificador o el email para el rate limiting
    client_ip = request.client.host
    identifier = f"{client_ip}:{email}"
    
    # Configuramos los límites, 5 solicitudes por hora
    if rate_limit_exceeded(redis_client, identifier, max_requests=5, period=3600):
        raise HTTPException(status_code=429, detail= "Rate limit exceeded, please try again later.")

    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="El usuario no existe.")
    
    # Genera el token con alguna información útil y un tiempo de expiración
    password_reset_token, expiry = await token_service.create_token(
        data={"sub": email, "aud": "password-recovery"}
    )
    
    token_service.insert_token(user_id=user.id, token= password_reset_token, expiry= expiry)

    # Envía el email en segundo plano
    background_tasks.add_task(
        send_reset_password_email, email_to=email, token=password_reset_token
    )

    return {"msg": "El enlace para restablecer tu contraseña ha sido enviado, por favor revisa tu email.",
            "token" : password_reset_token}


@router.put("/reset-password/")
async def reset_password(info: ResetPasswordFields, db: Session = Depends(get_db)):
    token_service = PasswordResetTokenService(db)
    user_service = UserService(db)

    email = await token_service.verify_token(info.token)
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if info.new_password != info.new_password_confirm:
        raise HTTPException(status_code= 400, detail= "Passwords don't match.")

    if len(info.new_password) < 7:
        raise HTTPException(status_code=400, detail="Password must be at least 7 characters long")

    user_update = UserUpdate(password= info.new_password)
    user_service.update_user(user_id= user.id, user_update= user_update)

    token_update= PasswordResetTokenUpdate(is_used= True)
    token_service.update_token(token= info.token, token_update=token_update)

    return {"message" : "The password has been updated succesfully"}
