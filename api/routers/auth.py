# --------------------- UTILS! ---------------------
from ..utils.auth_utils import authenticate_user, create_access_token
from ..utils.rate_limiting import rate_limit_exceeded

# --------------------- SERVICES! ---------------------
from ..services.user_service import UserService
from ..services.token_service import EmailConfirmationTokenService
from ..services.email_service import EmailService
from ..config.dependencies import get_current_user

from ..config.constants import ACCESS_TOKEN_EXPIRE_MINUTES, LOGIN_RATE_LIMIT_PERIOD, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_SECRET_CLIENT
from ..config.dependencies import oauth2_scheme

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from .. import schemas, models

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
    """
    Authenticate a user and issue an access token.

    This endpoint authenticates a user using their email and password, and issues a JWT access token if the credentials are valid.

    Args:
        response (Response): The response object to set cookies.
        request (Request): The request object to get the client's IP address.
        form_data (OAuth2PasswordRequestForm): The form data containing the user's email and password.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary containing the access token, token type, and user's email.

    Raises:
        HTTPException: If the rate limit is exceeded (status code 429).
        HTTPException: If the credentials are incorrect (status code 401).
    """
    username = form_data.username
    client_ip = request.client.host
    identifier = f"{client_ip}:{username}"

    if rate_limit_exceeded(redis_client= redis_client, identifier= identifier, max_requests= 5, period= LOGIN_RATE_LIMIT_PERIOD):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code= 401,
            detail="Incorrect email or password",
            headers= {"WWW-Authenticate": "Bearer"}
        )
        
    access_token_expires= timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data= {"sub": user.email}, expires_delta= access_token_expires)

    response.set_cookie(
        key="access_token",
        value= access_token,
        secure= False, # True in production
        samesite= 'Lax',
        max_age= ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True
    )

    return {"msg" : "User logged in successfully"}


@router.get("/login/google")
async def login_google(request: Request):
    """
    Redirect the user to Google's OAuth 2.0 login page.

    Args:
        request (Request): The request object to get the current URL.

    Returns:
        RedirectResponse: A response redirecting the user to the Google OAuth 2.0 login page.
    """
    url = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, url)


@router.get("/auth")
async def auth(response: Response, request: Request, db: Session= Depends(get_db)):
    """
    Handle the callback from Google OAuth 2.0 and authenticate the user.

    Args:
        response (Response): The response object to set cookies.
        request (Request): The request object containing the authorization response from Google.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary containing the access token, token type, and user's email.

    Raises:
        HTTPException: If the token could not be obtained from Google (status code 400).
    """
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
            user_created = user_service.create_user_google(schemas.UserCreateGoogle(
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
        secure=False,  # Must be True in production with HTTPS
        samesite='Lax',
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"msg" : "User logged in successfully"}


@router.post("/register", status_code= 201)
async def new_user_registration(user: schemas.UserCreate,db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint registers a new user, generates an email confirmation token, and sends a confirmation email to the user.

    Args:
        user (schemas.UserCreate): The data required to create a new user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message confirming successful registration and the generated token.

    Raises:
        HTTPException: If the email, phone number, or document is already registered (status code 400).
        HTTPException: If the password is less than 7 characters long (status code 400).
    """
    user_service = UserService(db)

    exists_email = user_service.get_user_by_email(user_email= user.email)
    exists_phone_number = user_service.get_user_by_phone_number(phone_number= user.phone_number) if user.phone_number is not None else None
    exists_document = user_service.get_user_by_document(document=user.document) if user.document is not None else None

    if exists_email:
         raise HTTPException(status_code=400, detail="Email alredy registered")
    
    elif exists_phone_number:
        raise HTTPException(status_code=400, detail="Phone number alredy registered")
    
    elif exists_document:
        raise HTTPException(status_code=400, detail="Document alredy registered")

    if len(user.plain_password) < 7:
        raise HTTPException(status_code=400, detail="Password must be at least 7 characters long.")

    user_created= user_service.create_user(user= user)

    token_service = EmailConfirmationTokenService(db)
    email_service = EmailService()

    # Generating email confirmation token
    token_data = {"sub" : user.email, "aud" : "email-confirmation"}
    token, expiry = await token_service.create_token(data= token_data)

    # Inserting the new token to the database
    token_service.insert_token(user_created.id, token, expiry)

    # Sending confirmation email
    await email_service.send_confirmation_account_message(user.email, token)

    return {"message" : "User registered successfully, please check your email to confirm your account."}


@router.patch("/confirm-user-account")
async def confirm_user_account(info: schemas.ConfirmBase, db: Session = Depends(get_db)):
    """
    Confirm the user's account using the provided token.

    Args:
        info (ConfirmBase): The token required to confirm the user's account.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message confirming that the user's account has been activated.

    Raises:
        HTTPException: If the user is not found (status code 404).
    """
    token_service = EmailConfirmationTokenService(db)
    email = await token_service.verify_token(info.token)
    
    user_service = UserService(db)
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail= "User not found.")
    
    user_update = schemas.UserUpdate(is_active=True)
    user_service.update_user(user.id, user_update)
    token_update = schemas.EmailConfirmationTokenUpdate(is_used=True)
    token_service.update_token(info.token, token_update)

    return {"message" : "User account activated successfully"}


@router.get("/get-token/confirm-user-account", dependencies=[Depends(oauth2_scheme)])
async def get_confirmation_token(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):    
    if current_user.is_active:
        raise HTTPException(status_code= 400, detail="Your account is alredy active.")
    
    token_service = EmailConfirmationTokenService(db)  
    email_service = EmailService()

    # Generating email confirmation token
    token_data = {"sub" : current_user.email, "aud" : "email-confirmation"}
    token, expiry = await token_service.create_token(data= token_data)

    # Inserting the new token to the database
    token_service.insert_token(current_user.id, token, expiry)

    # Sending confirmation email
    await email_service.send_confirmation_account_message(current_user.email, token)
