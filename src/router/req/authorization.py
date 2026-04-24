import logging
import uuid
from typing import Any, List

import jwt as jwt_util
from fastapi import Depends, Path, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...config.conf import JWT_ALGORITHM, ACCESS_TOKEN_TTL, SHORT_TERM_TTL
from ...config.exception import *
from ...infra.util.time_util import *

log = logging.getLogger(__name__)

auth_scheme = HTTPBearer()

def parse_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    if not token:
        log.error(f'parse_token fail: [\'token\' is required in credentials], credentials:{credentials}')
        raise UnauthorizedException(msg='Authorization failed')

    return token

def __get_secret(pattern: Any):
    return f'secret{str(pattern)[::-1]}' # if user_id != None else JWT_SECRET

def gen_token(data: dict, fields: List = []):
    public_info = {}
    if not 'user_id' in data:
        log.error(f'gen_token fail: [\'user_id\' is required in data], data:{data}, fields:{fields}')
        raise ServerException(msg='user_id not found in data')

    secret = __get_secret(data['user_id'])
    for field in fields:
        val = str(data[field])
        public_info[field] = val

    public_info.update({ 'exp': expiration_time() })
    return jwt_util.encode(payload=public_info, key=secret, algorithm=JWT_ALGORITHM)


def gen_token_by_pattern(pattern: Any):
    secret = __get_secret(pattern)
    public_info = { 'exp': expiration_time() }
    return jwt_util.encode(payload=public_info, key=secret, algorithm=JWT_ALGORITHM)


def expiration_time():
    return current_seconds() + ACCESS_TOKEN_TTL


def gen_refresh_token():
    prefix = str(uuid.uuid4()).replace('-', '')
    expiration = expiration_time()
    return f'{prefix[0:20]}{expiration}'

def valid_refresh_token(refresh_token: str) -> (bool):
    future_time_in_secs = int(refresh_token[-10:])
    current_time_in_secs = current_seconds()
    diff = abs(future_time_in_secs - current_time_in_secs)
    # 兩者誤差在過期時間的一半內，視為有效
    passed = diff < SHORT_TERM_TTL / 2
    log.info('\n\n\nfuture_t: %s, current_t: %s, diff: %s, passed: %s', future_time_in_secs, current_time_in_secs, diff, passed)
    return passed


def __jwt_decode(jwt, key, msg):
    try:
        algorithms = [JWT_ALGORITHM]
        return jwt_util.decode(jwt, key, algorithms)
    except Exception as e:
        log.error(f'__jwt_decode fail, key:{key}, algorithms:{algorithms}, msg:{msg}, jwt:{jwt}, \ne:{e}')
        raise UnauthorizedException(msg=msg)


def __valid_user_id(data: dict, user_id):
    if not 'user_id' in data:
        return False

    return int(data['user_id']) == int(user_id)


def __outdated_token(data: dict) -> (bool):
    if not 'exp' in data:
        return True

    future_time_in_secs = int(data['exp'])
    current_time_in_secs = current_seconds()
    log.info('\n\n\noutdated?? future_time_in_secs: %d, current_time_in_secs: %d', future_time_in_secs, current_time_in_secs)
    return not 'exp' in data or current_seconds() > future_time_in_secs


def __verify_token_in_auth(user_id: int, credentials: HTTPAuthorizationCredentials, err_msg: str):
    secret = __get_secret(user_id)
    token = parse_token(credentials)
    data = __jwt_decode(jwt=token, key=secret, msg=err_msg)

    if not __valid_user_id(data, user_id) or __outdated_token(data):
        raise UnauthorizedException(msg=err_msg)

def __extract_user_id_from_token(token: str) -> int:
    try:
        unverified = jwt_util.decode(
            token,
            options={"verify_signature": False},
            algorithms=[JWT_ALGORITHM],
        )
    except Exception:
        raise UnauthorizedException(msg='invalid token')

    user_id = unverified.get('user_id')
    if not user_id:
        raise UnauthorizedException(msg='user_id not found in token')
    return int(user_id)


def verify_jwt_access(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> int:
    token = parse_token(credentials)
    user_id = __extract_user_id_from_token(token)
    __verify_token_in_auth(user_id, credentials, 'access denied')
    return user_id


async def verify_path_user_id(
    request: Request,
    token_user_id: int = Depends(verify_jwt_access),
):
    path_user_id = request.path_params.get('user_id')
    if path_user_id is None:
        return
    if int(path_user_id) != int(token_user_id):
        raise ForbiddenException(msg='user_id not match')


def verify_query_user_id(
    user_id: int = Query(...),
    token_user_id: int = Depends(verify_jwt_access),
):
    if int(user_id) != int(token_user_id):
        raise ForbiddenException(msg='user_id not match')


def verify_token_by_update_password(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                                    user_id: int = Path(...),
                                    ):
    __verify_token_in_auth(user_id, credentials, 'access denied')


def verify_token_for_delete_account(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> int:
    token = parse_token(credentials)
    user_id = __extract_user_id_from_token(token)
    __verify_token_in_auth(user_id, credentials, 'access denied')
    return user_id
