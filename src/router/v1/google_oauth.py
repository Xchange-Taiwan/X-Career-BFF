import logging

from fastapi import APIRouter, Query, Body, Response
from fastapi.responses import RedirectResponse

from ..req.authorization import *
from ..res.response import *
from ...app._di.injection import _google_oauth_service

log = logging.getLogger(__name__)


router = APIRouter(
    prefix='/oauth/google',
    tags=['Google OAuth'],
    responses={404: {'description': 'Not found'}},
)

@router.post('/authorize/signup', status_code=201)
async def oauth_authorize_signup():
    data = await _google_oauth_service.get_authorization_url_by_signup()
    return post_success(data=data, msg='Authorization URL generated successfully!')

@router.post('/authorize/login', status_code=201)
async def oauth_authorize_login():
    data = await _google_oauth_service.get_authorization_url_by_login()
    return post_success(data=data, msg='Authorization URL generated successfully!')


@router.post('/callback', status_code=201)
async def oauth_callback(
    code: str = Body(..., embed=True),
    state: str = Body(..., embed=True),
):
    data = await _google_oauth_service.handle_callback(code, state)
    return post_success(data=data, msg='Authorization successful!')
