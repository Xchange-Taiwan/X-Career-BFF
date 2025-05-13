import json
from typing import Any, Dict, List, Set, Optional, Union
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo

from ...user.model.user_model import ProfileVO
from ....config.exception import ClientException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)

class GoogleAuthorizeDTO(BaseModel):
    email: EmailStr
    # redirect_uri: Optional[str] = None  # 可選的前端重定向 URI

