import logging

from fastapi import APIRouter, Query

from ..req.auth_validation import *
from ..req.authorization import *
from ..res.response import *
from ...app._di.injection import _oauth_service
from ...config.conf import DEFAULT_LANGUAGE_ENUM
from ...config.constant import Language, OAuthType
from ...domain.auth.service.auth_service import AuthService

log = logging.getLogger(__name__)


router = APIRouter(
    prefix='/oauth',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)

@router.post('/signup/{auth_type}', status_code=201)
async def signup_oauth(
    auth_type: OAuthType = Path(...),
    body: SignupOauthDTO = Body(...),
):
    if auth_type == OAuthType.GOOGLE:
        data = await _oauth_service.signup_oauth_google_and_send_email(body)
    else:
        raise ServerException(msg='Invalid auth type')
    return post_success(data=data, msg='Account signup successfully!')


@router.post('/login/{auth_type}',
             responses=post_response('login_oauth', LoginResponseVO),
             status_code=201)
async def login_oauth(
    auth_type: OAuthType = Path(...),
    body: LoginOauthDTO = Body(...),
    language: Language = Query(default=DEFAULT_LANGUAGE_ENUM)
):
    if auth_type == OAuthType.GOOGLE:
        data = await _oauth_service.login_oauth_google(body, language.value)
    else:
        raise ServerException(msg='Invalid auth type')
    return AuthService.auth_response(data=data)
