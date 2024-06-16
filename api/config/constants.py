from dotenv import load_dotenv
import os

load_dotenv()

# -------------------------- SECRET KEYS --------------------------
EMAIL_CONFIRMATION_SECRET_KEY = os.getenv("EMAIL_CONFIRMATION_SECRET_KEY")
PASSWORD_RESET_SECRET_KEY = os.getenv("PASSWORD_RESET_SECRET_KEY")
ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")
GOOGLE_OAUTH_SECRET_CLIENT = os.getenv("GOOGLE_OAUTH_SECRET_CLIENT")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

# -------------------------- ALGORITHMS --------------------------
ALGORITHM = os.getenv("ALGORITHM")


# -------------------------- EXPIRATION TOKENS TIME --------------------------
ACCESS_TOKEN_EXPIRE_MINUTES=10
RESET_TOKEN_EXPIRE_MINUTES = 10
CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES = 4


# -------------------------- ZOOM CONFIGURATION --------------------------
MAIL_USERNAME= os.getenv('MAIL_USERNAME')
MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
MAIL_FROM= os.getenv('MAIL_FROM')


# -------------------------- DATABASE CONFIGURATION --------------------------
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')


