import logging

from pydantic import BaseModel, EmailStr

log = logging.getLogger(__name__)

class GoogleAuthorizeDTO(BaseModel):
    email: EmailStr
    # redirect_uri: Optional[str] = None  # 可選的前端重定向 URI

