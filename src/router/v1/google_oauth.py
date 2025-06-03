from typing import List, Dict, Any
from fastapi import (
    APIRouter,
    Request, Depends,
    Cookie, Header, Path, Query, Body, Form
)

from ...config.conf import DEFAULT_LANGUAGE_ENUM
from ...config.constant import Language
from ...config.exception import *
from ...domain.auth.model.auth_model import *
from ...domain.auth.model.google_oauth_model import *
from ...domain.auth.service.auth_service import AuthService
from ..req.auth_validation import *
from ..req.authorization import *
from ..res.response import *
from ...app._di.injection import _google_oauth_service
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix='/oauth/google',
    tags=['Google OAuth'],
    responses={404: {'description': 'Not found'}},
)

@router.post('/authorize/signup', status_code=201)
async def oauth_authorize_signup(
    body: GoogleAuthorizeDTO = Body(...),
):
    data = await _google_oauth_service.get_authorization_url_by_signup(body.email)
    return post_success(data=data, msg='Authorization URL generated successfully!')


@router.post('/authorize/login', status_code=201)
async def oauth_authorize_login(
    body: GoogleAuthorizeDTO = Body(...),
):
    data = await _google_oauth_service.get_authorization_url_by_login(body.email)
    return post_success(data=data, msg='Authorization URL generated successfully!')


@router.get('/callback', status_code=200)
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
):
    data = await _google_oauth_service.handle_callback(code, state)
    return res_success(data=data, msg='Authorization successful!')
