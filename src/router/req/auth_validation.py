from typing import Optional

from fastapi import Body, Form, Request

from ...domain.auth.model.auth_model import *


def login_check_body(
    body: LoginDTO = Body(...)
) -> (LoginDTO):
    # TODO: verify the password characters
    return body


def oauth_refresh_token_grant(
    request: Request,
    grant_type: str = Form(..., description='OAuth 2.0：必須為 refresh_token'),
    refresh_token: Optional[str] = Form(
        None,
        description='先前核發的 refresh token；若為 HttpOnly cookie 則可省略，改由瀏覽器自動帶上同名 cookie',
    ),
) -> str:
    """RFC 6749 Section 6：`grant_type` + `refresh_token`（form）；`refresh_token` 可改由 HttpOnly cookie 提供。"""
    if grant_type != 'refresh_token':
        raise ClientException(msg='unsupported_grant_type')
    rt = (refresh_token or '').strip()
    if not rt:
        rt = (request.cookies.get('refresh_token') or '').strip()
    if not rt:
        raise ClientException(msg='invalid_request')
    return rt