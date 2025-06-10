import logging as log

from pydantic import BaseModel, EmailStr

log.basicConfig(filemode='w', level=log.INFO)

class GoogleAuthorizeDTO(BaseModel):
    email: EmailStr
    # redirect_uri: Optional[str] = None  # 可選的前端重定向 URI

