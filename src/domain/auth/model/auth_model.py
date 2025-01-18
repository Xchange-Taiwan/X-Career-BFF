import json
from typing import Any, Dict, List, Set, Optional, Union
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo

from ...user.model.user_model import ProfileVO
from ....config.exception import ClientException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SignupDTO(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    def passwords_match(cls, v, values: ValidationInfo):
        if 'password' in values.data and v != values.data['password']:
            raise ClientException(msg='passwords do not match')
        return v

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
                'confirm_password': 'secret',
            },
        }


class SignupOauthDTO(BaseModel):
    email: EmailStr
    oauth_id: str
    access_token: str

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'user@example.com',
                'oauth_id': 'oauth_id',
                'access_token': 'access_token',
            },
        }


class SignupConfirmDTO(BaseModel):
    region: Optional[str] = 'jp'
    email: EmailStr
    token: str

    class Config:
        json_schema_extra = {
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
        json_schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
            },
        }


class LoginOauthDTO(BaseModel):
    oauth_id: str
    access_token: str

    class Config:
        json_schema_extra = {
            'example': {
                'oauth_id': 'oauth_id',
                'access_token': 'access_token',
            },
        }


class SSOLoginDTO(BaseModel):
    code: str
    state: str
    sso_type: Optional[str]

    def to_dict(self):
        d = super().model_dump()
        d.pop('sso_type', None)
        return d


class NewTokenDTO(BaseModel):
    user_id: int
    refresh_token: str


class ResetPasswordDTO(BaseModel):
    register_email: EmailStr
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    def passwords_match(cls, v, values: ValidationInfo):
        if 'password' in values.data and v != values.data['password']:
            raise ClientException(msg='passwords do not match')
        return v

    class Config:
        json_schema_extra = {
            'example': {
                'register_email': 'user@example.com',
                'password': 'secret',
                'confirm_password': 'secret',
            },
        }


class UpdatePasswordDTO(ResetPasswordDTO):
    origin_password: str

    class Config:
        json_schema_extra = {
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
    user: ProfileVO
