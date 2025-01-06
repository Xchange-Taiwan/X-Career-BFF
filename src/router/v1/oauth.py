from typing import List, Dict, Any
from pydantic import EmailStr
from fastapi import (
    APIRouter,
    Request, Depends,
    Cookie, Header, Path, Query, Body, Form
)

from ...config.conf import DEFAULT_LANGUAGE
from ...config.constant import OauthType
from ...config.exception import *
from ...domain.auth.model.auth_model import *
from ...domain.auth.service.auth_service import AuthService
from ..req.auth_validation import *
from ..req.authorization import *
from ..res.response import *
from ...app._di.injection import _oauth_service
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix='/oauth',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)

@router.post('/signup/{auth_type}', status_code=201)
async def signup_oauth(
    auth_type: OauthType = Path(...),
    body: SignupOauthDTO = Body(...),
):
    if auth_type == OauthType.GOOGLE:
        data = await _oauth_service.signup_oauth_google(body)
    else:
        raise ServerException(msg='Invalid auth type', data=self.ttl_secs)
    return post_success(data=data, msg='Account signup successfully!')

@router.post('/login/{auth_type}', status_code=201)
async def login_oauth(
    auth_type: OauthType = Path(...),
    body: LoginOauthDTO = Body(...),
    language: str = Query(default=DEFAULT_LANGUAGE)
):
    if auth_type == OauthType.GOOGLE:
        data = await _oauth_service.login_oauth_google(body, language)
    else:
        raise ServerException(msg='Invalid auth type', data=self.ttl_secs)
    return post_success(data=data, msg='Account login successfully!')
