from typing import List, Dict, Any
from pydantic import EmailStr
from fastapi import (
    APIRouter,
    Request, Depends,
    Cookie, Header, Path, Query, Body, Form
)
from ...domain.auth.model.auth_model import *
from ...domain.auth.service.auth_service import AuthService
from ..req.auth_validation import *
from ..req.authorization import *
from ..res.response import *
from ...config.exception import *
from ...config.region_host import get_auth_region_host, get_user_region_host
from ...config.service_client import service_client
from ...config.cache import gw_cache
import logging as log

log.basicConfig(filemode='w', level=log.INFO)

auth_host = get_auth_region_host()
user_host = get_user_region_host()
_auth_service = AuthService(
    service_client, 
    gw_cache,
)

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/signup', status_code=201)
async def signup(
    body: SignupDTO = Body(...),
):
    data = await _auth_service.signup(auth_host, body)
    return post_success(data=data, msg='email_sent')


@router.post('/email/resend', status_code=201)
async def signup_email_resend(
    email: EmailStr = Body(..., embed=True),
):
    data = await _auth_service.signup_email_resend(auth_host, email)
    return post_success(data=data, msg='Verification email has been resent successfully.')


@router.post('/signup/confirm',
             responses=post_response('confirm_signup', SignupResponseVO),
             status_code=201)
async def confirm_signup(
    token: str = Body(..., embed=True),
):
    data = await _auth_service.confirm_signup(auth_host, token)
    return post_success(data=data, msg='Confirming successful signup.')


@router.post('/login',
             responses=post_response('login', LoginResponseVO),
             status_code=201)
async def login(
    body: LoginDTO = Depends(login_check_body),
):
    data = await _auth_service.login(auth_host, user_host, body)
    return post_success(data=data)


@router.post('/token',
             status_code=201)
async def refresh_token(
    body: NewTokenDTO = Body(...),
):
    data = await _auth_service.get_new_token_pair(body)
    return post_success(data=data)


@router.post('/logout', status_code=201)
async def logout(
    user_id: int = Body(..., embed=True),
):
    data, msg = await _auth_service.logout(user_id)
    return post_success(data=data, msg=msg)


@router.put('/password/{user_id}/update')
async def update_password(
    user_id: int = Path(...),
    update_password_dto: UpdatePasswordDTO = Body(...),
    verify=Depends(verify_token_by_update_password),
):
    await _auth_service.update_password(auth_host, user_id, update_password_dto)
    return res_success(msg='update success')


@router.get('/password/reset/email')
async def send_reset_password_comfirm_email(
    email: EmailStr,
):
    data = await _auth_service.send_reset_password_comfirm_email(auth_host, email)
    return res_success(data=data, msg='send_email_success')


@router.put('/password/reset')
async def reset_password(
    reset_passwrod_dto: ResetPasswordDTO = Body(...),
    verify_token: str = Query(...),
):
    await _auth_service.reset_passwrod(auth_host, verify_token, reset_passwrod_dto)
    return res_success(msg='reset success')
