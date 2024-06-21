from fastapi import HTTPException

credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

expired_token_exception = HTTPException(
        status_code=401,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"}
    )

class PatchMeetingError(Exception):
    pass

class DeleteMeetingError(Exception):
    pass