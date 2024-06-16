from sqlalchemy.orm import Session
from .. import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException

crypt = CryptContext(schemes= ["bcrypt"])


class UserService:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> models.User:
        return self.db.query(models.User).filter(models.User.id == user_id).first()


    def get_user_by_email(self, user_email: str) -> models.User:
        return self.db.query(models.User).filter(models.User.email == user_email).first()


    def get_user_by_username(self, username: str) -> models.User:
        return self.db.query(models.User).filter(models.User.username == username).first()


    def get_user_by_phone_number(self, phone_number: str) -> models.User:
        return self.db.query(models.User).filter(models.User.phone_number == phone_number).first()


    def get_user_by_document(self, document: str) -> models.User:
        return self.db.query(models.User).filter(models.User.document == document).first()


    def create_user(self, user: schemas.UserCreate) -> models.User:
        password_hash = crypt.hash(user.plain_password)
        db_user = models.User(
            first_name= user.first_name,
            second_name= user.second_name,
            lastname= user.lastname,
            email= user.email,
            phone_number= user.phone_number,
            document= user.document,
            password_hash= password_hash)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user


    def update_user(self, user_id: int, user_update: schemas.UserUpdate) -> models.User:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        self.check_unique_constraints(db_user, user_update)
        
        update_data = user_update.model_dump(exclude_unset=True)

        if "plain_password" in update_data:
            password_hash = crypt.hash(update_data.get("plain_password"))
            update_data["password_hash"] = password_hash
            del update_data["plain_password"]
        
        for key, value in update_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user


    def delete_user(self, user_id: int) -> models.User:
        db_user = self.get_user_by_id(user_id)
        if db_user is None:
            return None
        
        self.db.delete(db_user)
        self.db.commit()
        return db_user


    def check_unique_constraints(self, db_user: models.User ,user_update: schemas.UserUpdate) -> None:

        # Verifica si hay un correo electrónico diferente con el mismo valor
        if user_update.email and user_update.email != db_user.email:
            exists_email = self.get_user_by_email(user_update.email)
            if exists_email:
                raise HTTPException(status_code=400, detail="Email already registered")

        # Verifica si hay un número de teléfono diferente con el mismo valor
        if user_update.phone_number and user_update.phone_number != db_user.phone_number:
            exists_phone_number = self.get_user_by_phone_number(user_update.phone_number)
            if exists_phone_number:
                raise HTTPException(status_code=400, detail="Phone number already registered")