from fastapi import HTTPException, status

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"}
    )

class GetMeetingError(Exception):
    pass

class CreateMeetingError(Exception):
    pass

class PatchMeetingError(Exception):
    pass

class DeleteMeetingError(Exception):
    pass