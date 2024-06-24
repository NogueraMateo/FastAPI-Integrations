from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from ..utils.auth_utils import get_current_admin_user
from .. import models, schemas
from ..database import get_db
from ..services.user_service import AdminService

router = APIRouter(tags=["Special Routes"])

@router.get("/admin/read-user/{user_id}", response_model= schemas.User)
async def read_user_by_id(user_id: int, current_user: models.User= Depends(get_current_admin_user), db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    return admin_service.get_user_by_id(user_id) 


@router.put("/admin/modify-user-account/{user_id}", response_model= schemas.User)
async def modify_user_account(user_id: int, user_update: schemas.UserUpdate, current_user: models.User= Depends(get_current_admin_user), db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    return admin_service.update_user(user_id, user_update)


@router.post("/admin/create-new-account", response_model= schemas.User)
async def create_new_account(user_create: schemas.UserCreateByAdmin, current_user: models.User= Depends(get_current_admin_user), db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    return admin_service.create_user(user_create)


@router.delete("/admin/delete-user-account/{user_id}", response_model= schemas.User)
async def delete_user_account(user_id: int, current_user: models.User= Depends(get_current_admin_user), db: Session = Depends(get_db)):
    admin_service = AdminService(db)
    return admin_service.delete_user(user_id)


@router.get("/admin/read-users", response_model= List[schemas.User])
async def read_users(current_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    return db.query(models.User).filter().all()