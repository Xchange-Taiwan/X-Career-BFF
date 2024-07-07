import functools
import time

from starlette import status

from ...domain.cache import ICache
from ...config.constant import SERIAL_KEY
from ...config.exception import ServerException, ClientException, UnauthorizedException, ForbiddenException, \
    NotFoundException, NotAcceptableException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


def gen_confirm_code():
    code = int(time.time() ** 6 % 1000000)
    code = code if (code > 100000) else code + 100000
    log.info(f'confirm_code: {code}')
    return code


def get_serial_num(cache: ICache, user_id: str):
    user = cache.get(user_id)
    if not user or not SERIAL_KEY in user:
        log.error(f'get_serial_num fail: [user has no \'SERIAL_KEY\'], user_id:%s', user_id)
        raise ServerException(msg='user has no authrozanization')

    return user[SERIAL_KEY]




def check_response_code(method: str, expected_code: int = 200):
    def decorator_check_response_code(func):
        @functools.wraps(func)
        async def wrapper_check_response_code(*args, **kwargs):
            function_name: str = func.__name__
            url = kwargs.get('url', None)
            params = kwargs.get('params', None)
            body = kwargs.get('json', None)
            headers = kwargs.get('headers', None)
            try:
                response = await func(*args, **kwargs)
                status_code = int(response.get('code', None)) #回傳為res_sucess/ res_error型態
                if status_code < 400 or response.status_code == expected_code:
                    return response

                response_json = response.json()
                msg = response_json["msg"] if "msg" in response_json else response.reason
                data = response_json["data"] if "data" in response_json else None
                log.error(
                    f"service request fail, [%s]: %s, body:%s, params:%s, headers:%s, status_code:%s, msg:%s, \n response:%s",
                    method, url, body, params, headers, status_code, msg, response)

                if status_code == status.HTTP_400_BAD_REQUEST:
                    raise ClientException(msg=msg, data=data)

                if status_code == status.HTTP_401_UNAUTHORIZED:
                    raise UnauthorizedException(msg=msg, data=data)

                if status_code == status.HTTP_403_FORBIDDEN:
                    raise ForbiddenException(msg=msg, data=data)

                if status_code == status.HTTP_404_NOT_FOUND:
                    raise NotFoundException(msg=msg, data=data)

                if status_code == status.HTTP_406_NOT_ACCEPTABLE:
                    raise NotAcceptableException(msg=msg, data=data)

                raise ServerException(msg=msg, data=data)
            except Exception as e: #這邊捕捉非Server response 狀態錯誤(有正常回傳resp)的情況
                err_msg: str = f"unhandled {function_name} request error, {url}, {params}, {headers}"
                log.error(err_msg)
                raise ServerException(msg=err_msg)

        return wrapper_check_response_code

    return decorator_check_response_code
