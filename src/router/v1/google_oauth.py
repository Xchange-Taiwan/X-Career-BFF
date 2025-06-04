import logging as log

from fastapi import APIRouter, Query

from ..req.authorization import *
from ..res.response import *
from ...app._di.injection import _google_oauth_service

log.basicConfig(filemode='w', level=log.INFO)


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


@router.get('/callback', status_code=200)
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
):
    data = await _google_oauth_service.handle_callback(code, state)
    return res_success(data=data, msg='Authorization successful!')
