from fastapi import Request, Body

from ...domain.auth.model.auth_model import *


def login_check_body(
    body: LoginDTO = Body(...)
) -> (LoginDTO):
    # TODO: verify the password characters
    return body

def refresh_token_check(
    request: Request,
    user_id: int = Body(..., embed=True),
) -> (NewTokenDTO):
    refresh_token = request.cookies.get('refresh_token')
    if refresh_token is None:
        raise ClientException(msg='refresh_token is required in the cookies')
    
    return NewTokenDTO(
        user_id=user_id,
        refresh_token=refresh_token,
    )