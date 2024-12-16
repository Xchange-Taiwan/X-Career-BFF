import json
from typing import Any, Dict, List, Set, Optional, Union
from pydantic import BaseModel, EmailStr, validator
from ....config.exception import ClientException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SignupDTO(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ClientException(msg='passwords do not match')
        return v

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
                'confirm_password': 'secret',
            },
        }


class SignupConfirmDTO(BaseModel):
    region: Optional[str] = 'jp'
    email: EmailStr
    token: str

    class Config:
        schema_extra = {
            'example': {
                'region': 'ap-northeast-1',
                'email': 'user@example.com',
                'token': '1e3162f7-77b6-4ea4-b8b1-8f9439ac3789',
            },
        }


class LoginDTO(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
            },
        }


class SSOLoginDTO(BaseModel):
    code: str
    state: str
    sso_type: Optional[str]

    def to_dict(self):
        d = super().dict()
        d.pop('sso_type', None)
        return d


class NewTokenDTO(BaseModel):
    user_id: int
    refresh_token: str


class ResetPasswordDTO(BaseModel):
    register_email: EmailStr
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ClientException(msg='passwords do not match')
        return v

    class Config:
        schema_extra = {
            'example': {
                'register_email': 'user@example.com',
                'password': 'secret',
                'confirm_password': 'secret',
            },
        }


class UpdatePasswordDTO(ResetPasswordDTO):
    origin_password: str

    class Config:
        schema_extra = {
            'example': {
                'register_email': 'user@example.com',
                'password': 'secret2',
                'confirm_password': 'secret2',
                'origin_password': 'secret',
            },
        }


class BaseAuthDTO(BaseModel):
    # registration region
    region: str
    user_id: int


class AuthVO(BaseAuthDTO):
    email: EmailStr
    token: str
    online: Optional[bool] = False
    created_at: int


class SignupResponseVO(BaseModel):
    auth: AuthVO


class LoginResponseVO(SignupResponseVO):
    # TODO: define user VO
    user: Dict
