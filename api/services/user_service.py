from sqlalchemy.orm import Session
from .. import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException

crypt = CryptContext(schemes= ["bcrypt"])


class UserService:
    """
    A service class for managing user-related operations.

    Attributes:
        db (Session): The database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the UserService with the provided database session.

        Args:
            db (Session): The database session.
        """
        self.db = db

    def get_user_by_id(self, user_id: int) -> models.User:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            models.User: The user with the specified ID, or None if not found.
        """
        return self.db.query(models.User).filter(models.User.id == user_id).first()


    def get_user_by_email(self, user_email: str) -> models.User:
        """
        Retrieve a user by their email address.

        Args:
            user_email (str): The email address of the user.

        Returns:
            models.User: The user with the specified email, or None if not found.
        """
        return self.db.query(models.User).filter(models.User.email == user_email).first()


    def get_user_by_phone_number(self, phone_number: str) -> models.User:
        """
        Retrieve a user by their phone number.

        Args:
            phone_number (str): The phone number of the user.

        Returns:
            models.User: The user with the specified phone number, or None if not found.
        """
        return self.db.query(models.User).filter(models.User.phone_number == phone_number).first()


    def get_user_by_document(self, document: str) -> models.User:
        """
        Retrieve a user by their document.

        Args:
            document (str): The document of the user.

        Returns:
            models.User: The user with the specified document, or None if not found.
        """
        return self.db.query(models.User).filter(models.User.document == document).first()


    def create_user(self, user: schemas.UserCreate) -> models.User:
        """
        Create a new user.

        Args:
            user (schemas.UserCreate): The user data for creating a new user.

        Returns:
            models.User: The newly created user.
        """
        data = user.model_dump(exclude_unset=True)
        
        password_hash = crypt.hash(user.plain_password) if "plain_password" in data else None

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


    def create_user_google(self, user: schemas.UserCreateGoogle) -> models.User:
        """
        Create a new user.

        Args:
            user (schemas.UserCreate): The user data for creating a new user.

        Returns:
            models.User: The newly created user.
        """
        data = user.model_dump(exclude_unset=True)
        
        password_hash = crypt.hash(user.plain_password) if "plain_password" in data else None

        db_user = models.User(
            first_name= user.first_name,
            second_name= user.second_name,
            lastname= user.lastname,
            email= user.email,
            phone_number= user.phone_number,
            document= user.document,
            password_hash= password_hash,
            google_access_token= user.google_access_token)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    

    def update_user(self, user_id: int, user_update: schemas.UserUpdate) -> models.User:
        """
        Update an existing user.

        Args:
            user_id (int): The ID of the user to update.
            user_update (schemas.UserUpdate): The updated user data.

        Returns:
            models.User: The updated user.

        Raises:
            HTTPException: If the user is not found or if there are unique constraint violations.
        """
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
        """
        Delete an existing user.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            models.User: The deleted user, or None if the user was not found.
        """
        db_user = self.get_user_by_id(user_id)
        if db_user is None:
            return None
        
        self.db.delete(db_user)
        self.db.commit()
        return db_user


    def check_unique_constraints(self, db_user: models.User ,user_update: schemas.UserUpdate) -> None:
        """
        Check for unique constraint violations when updating a user.

        Args:
            db_user (models.User): The current user in the database.
            user_update (schemas.UserUpdate): The updated user data.

        Raises:
            HTTPException: If there are unique constraint violations for email or phone number.
        """

        if user_update.email and user_update.email != db_user.email:
            exists_email = self.get_user_by_email(user_update.email)
            if exists_email:
                raise HTTPException(status_code=400, detail="Email already registered")

        if user_update.phone_number and user_update.phone_number != db_user.phone_number:
            exists_phone_number = self.get_user_by_phone_number(user_update.phone_number)
            if exists_phone_number:
                raise HTTPException(status_code=400, detail="Phone number already registered")



class AdminService(UserService):
    """
    A service class for managing admin-related user operations, extending the functionality of UserService.

    Attributes:
        db (Session): The database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the AdminService with the provided database session.

        Args:
            db (Session): The database session.
        """

        super().__init__(db)

    def create_user(self, user: schemas.UserCreateByAdmin) -> models.User:
        """
        Create a new user with admin privileges.

        Args:
            user (schemas.UserCreateByAdmin): The user data for creating a new user.

        Returns:
            models.User: The newly created user.

        Raises:
            HTTPException: If there are unique constraint violations for email, phone number, or document.
        """

        data = user.model_dump(exclude_unset=True)
        
        password_hash = crypt.hash(user.plain_password) if "plain_password" in data else None

        db_user = models.User(
            first_name= user.first_name,
            second_name= user.second_name,
            lastname= user.lastname,
            email= user.email,
            phone_number= user.phone_number,
            document= user.document,
            password_hash= password_hash,
            role= user.role,
            google_access_token= user.google_access_token)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user