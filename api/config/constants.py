from dotenv import load_dotenv
import os

load_dotenv()

# -------------------------- SECRET KEYS --------------------------
EMAIL_CONFIRMATION_SECRET_KEY = os.getenv("EMAIL_CONFIRMATION_SECRET_KEY")
PASSWORD_RESET_SECRET_KEY = os.getenv("PASSWORD_RESET_SECRET_KEY")
ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")

GOOGLE_OAUTH_SECRET_KEY = os.getenv("GOOGLE_OAUTH_SECRET_KEY")
GOOGLE_OAUTH_SECRET_CLIENT = os.getenv("GOOGLE_OAUTH_SECRET_CLIENT")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

# -------------------------- ALGORITHMS --------------------------
ALGORITHM = os.getenv("ALGORITHM")


# -------------------------- EXPIRATION TOKENS TIME --------------------------
ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES"))
CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES = float(os.getenv("CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES"))


# -------------------------- ZOOM CONFIGURATION --------------------------
MAIL_USERNAME= os.getenv('MAIL_USERNAME')
MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
MAIL_FROM= os.getenv('MAIL_FROM')


# -------------------------- DATABASE CONFIGURATION --------------------------
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')


# -------------------------- ON STARTUP ADMIN USER AND ADVISOR --------------------------
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADVISOR_EMAIL = os.getenv('ADVISOR_EMAIL')
ADVISOR_NAME = os.getenv('ADVISOR_NAME')

# -------------------------- RATE LIMITING --------------------------
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD"))

