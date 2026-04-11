import logging
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.domain.user.model.user_model import ProfileVO

log = logging.getLogger(__name__)


class GoogleAuthorizeDTO(BaseModel):
    email: EmailStr
    # redirect_uri: Optional[str] = None  # 可選的前端重定向 URI


class GoogleAuthorizeVO(BaseModel):
    """Returned by /authorize/signup and /authorize/login."""
    authorization_url: str
    state: str


class GoogleCallbackAuthVO(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    token: Optional[str] = None
    region: Optional[str] = None
    created_at: Optional[int] = None
    online: Optional[bool] = None


class GoogleCallbackVO(BaseModel):
    """Returned by /callback. auth_type is SIGNUP or LOGIN.
    For LOGIN, user is populated. For SIGNUP, ttl_secs is populated."""
    auth_type: str
    auth: GoogleCallbackAuthVO
    user: Optional[ProfileVO] = None
    ttl_secs: Optional[int] = None

