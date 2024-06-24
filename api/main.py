from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal
from . import models
from fastapi.middleware.cors import CORSMiddleware
from .routers import password_reset, meetings, auth, admins
from starlette.middleware.sessions import SessionMiddleware
from .config.constants import GOOGLE_OAUTH_SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD_HASH, ADVISOR_EMAIL, ADVISOR_NAME
from contextlib import asynccontextmanager

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    db: Session = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
        advisor = db.query(models.Advisor).filter(models.Advisor.email == ADVISOR_EMAIL).first()
        if not admin:
            admin = models.User(
                first_name="Matheww", 
                lastname="Drawer", 
                email=ADMIN_EMAIL, 
                password_hash =ADMIN_PASSWORD_HASH, # Password is admin123
                is_active=True,
                role='ADMIN'
            )
            db.add(admin)
            db.commit()
        
        if not advisor:
            advisor = models.Advisor(name= ADVISOR_NAME, email=ADVISOR_EMAIL)
            db.add(advisor)
            db.commit()
        yield
    finally:
        db.close()


app = FastAPI(lifespan= lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

app.add_middleware(SessionMiddleware, secret_key= GOOGLE_OAUTH_SECRET_KEY)
app.include_router(auth.router)
app.include_router(password_reset.router)
app.include_router(meetings.router)
app.include_router(admins.router)


# uvicorn backend.api.main:app --reload
@app.get("/")
async def root():
    return {"message": "Server raised"}