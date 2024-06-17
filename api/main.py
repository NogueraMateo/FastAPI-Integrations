from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth
from fastapi.middleware.cors import CORSMiddleware
from .routers import password_reset
from .routers import meetings
from starlette.middleware.sessions import SessionMiddleware
from .config.constants import GOOGLE_OAUTH_SECRET_KEY


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

app.add_middleware(SessionMiddleware, secret_key= GOOGLE_OAUTH_SECRET_KEY)
app.include_router(auth.router)
app.include_router(password_reset.router)
app.include_router(meetings.router)


# uvicorn backend.api.main:app --reload
@app.get("/")
async def root():
    return {"message": "Server raised"}