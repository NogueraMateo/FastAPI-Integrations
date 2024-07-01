from fastapi.security.base import SecurityBase
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi import Request
from .exceptions import credentials_exception

class OAuth2PasswordBearerWithCookie(SecurityBase):
    def __init__(self, *, auto_error: bool = True):
        self.model = APIKey(
            **{"name": "access_token", "in": APIKeyIn.cookie}
        )
        self.scheme_name = self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            if self.auto_error:
                raise credentials_exception
            else:
                return None
        return token

oauth2_scheme = OAuth2PasswordBearerWithCookie()