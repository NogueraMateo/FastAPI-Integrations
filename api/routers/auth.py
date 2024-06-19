# --------------------- UTILS! ---------------------
from ..utils.auth_utils import authenticate_user, create_access_token
from ..utils.rate_limiting import rate_limit_exceeded

# --------------------- SERVICES! ---------------------
from ..services.user_service import UserService
from ..services.token_service import EmailConfirmationTokenService
from ..services.email_service import EmailService

from ..config.constants import ACCESS_TOKEN_EXPIRE_MINUTES

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..config.constants import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_SECRET_CLIENT

from ..database import get_db
from .. import schemas

from sqlalchemy.orm import Session
from datetime import timedelta

import redis

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from starlette.responses import Response


oauth = OAuth()

oauth.register(
    name='google',
    client_id=GOOGLE_OAUTH_CLIENT_ID,
    client_secret=GOOGLE_OAUTH_SECRET_CLIENT,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'email openid profile',
    },
    redirect_uri = 'http://localhost:8000/auth'
)

router = APIRouter(tags=["Login and Registration"])
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses= True)

@router.post("/login")
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm= Depends(),
    db: Session= Depends(get_db)
    ):
    '''Retrieves the data from the form, authenticates the user and generates an access token for it'''

    username = form_data.username
    client_ip = request.client.host
    identifier = f"{client_ip}:{username}"

    if rate_limit_exceeded(redis_client= redis_client, identifier= identifier, max_requests= 5, period= 300):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code= 401,
            detail="Incorrect email or password",
            headers= {"WWW-Authenticate": "Bearer"}
        )
    
    # Elimina el conteo de intentos fallidos una vez el usuario se autentica correctamente.
    redis_client.delete(identifier)

    access_token_expires= timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data= {"sub": user.email}, expires_delta= access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value= access_token,
        secure= False, # This value must be true in production environment with HTTPS
        samesite= 'Lax',
        max_age= ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "access_token": access_token,
        "token-type": "Bearer",
        "email" : user.email
    }


@router.get("/login/google")
async def login_google(request: Request):
    url = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, url)


@router.get("/auth")
async def auth(response: Response, request: Request, db: Session= Depends(get_db)):
    try:
        res = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail="No se pudo obtener el token")

    user_info = res.get('userinfo')
    google_access_token = res.get('access_token')

    if user_info:
        user_email = user_info['email']
        user_first_name = user_info['given_name']
        user_lastname = user_info['family_name']

        user_service = UserService(db)
        user_db = user_service.get_user_by_email(user_email)

        if not user_db:
            user_created = user_service.create_user(schemas.UserCreate(
                first_name=user_first_name,
                lastname=user_lastname,
                email=user_email,
                google_access_token=google_access_token
            ))
            token_service = EmailConfirmationTokenService(db)
            email_service = EmailService()

            # Generating email confirmation token
            token_data = {"sub" : user_created.email, "aud" : "email-confirmation"}
            token, expiry = await token_service.create_token(data= token_data)

            # Inserting the new token to the database
            token_service.insert_token(user_created.id, token, expiry)

            # Sending confirmation email
            await email_service.send_confirmation_account_message(user_created.email, token)
 
        else:
            user_service.update_user(user_db.id, schemas.UserUpdate(google_access_token=google_access_token))
    
    access_token = await create_access_token(data={"sub": user_email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=False,  # Debe ser True en producción con HTTPS
        samesite='Lax',
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "access_token": access_token,
        "token-type": "Bearer",
        "email": user_email
    }


@router.post("/register", status_code= 201)
async def new_user_registration(user: schemas.UserCreate,db: Session = Depends(get_db)):
    '''User must provide:
        - First name
        - Second name (Optionally)
        - Lastname
        - Username
        - Email
        - Phone number
        - Document
        - Password '''
    
    user_service = UserService(db)
    token_service = EmailConfirmationTokenService(db)
    email_service = EmailService()

    exists_email = user_service.get_user_by_email(user_email= user.email)
    exists_phone_number = user_service.get_user_by_phone_number(phone_number= user.phone_number)
    exists_document = user_service.get_user_by_document(document=user.document)

    if exists_email:
         raise HTTPException(status_code=400, detail="Email alredy registered")
    
    elif exists_phone_number:
        raise HTTPException(status_code=400, detail="Phone number alredy registered")
    
    elif exists_document:
        raise HTTPException(status_code=400, detail="Document alredy registered")

    if len(user.plain_password) < 7:
        raise HTTPException(status_code=400, detail="Password must be at least 7 characters long.")

    user_created= user_service.create_user(user= user)

    # Generating email confirmation token
    token_data = {"sub" : user.email, "aud" : "email-confirmation"}
    token, expiry = await token_service.create_token(data= token_data)

    # Inserting the new token to the database
    token_service.insert_token(user_created.id, token, expiry)

    # Sending confirmation email
    await email_service.send_confirmation_account_message(user.email, token)

    return {"message" : "User registered successfully, please check your email to confirm your account.",
            "token" : token}


class ConfirmBase(BaseModel):
    token: str

@router.put("/confirm-user-account")
async def confirm_user_account(info: ConfirmBase, db: Session = Depends(get_db)):
    user_service = UserService(db)
    token_service = EmailConfirmationTokenService(db)
    email = await token_service.verify_token(info.token)

    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail= "User not found.")
    
    user_update = schemas.UserUpdate(is_active=True)
    user_service.update_user(user.id, user_update)
    token_update = schemas.EmailConfirmationTokenUpdate(is_used=True)
    token_service.update_token(info.token, token_update)

    return {"message" : "User account activated successfully"}