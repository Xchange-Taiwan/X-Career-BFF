import functools
import time
from typing import Dict

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
            err: str = ''
            try:
                service_api_res = await func(*args, **kwargs)
                # 代表是simple系列
                if type(service_api_res) is not tuple:
                    return service_api_res
                data: Dict = service_api_res[0]
                msg: str = service_api_res[1]
                err: str = service_api_res[2]
                #ex: 40400 取至404
                status_code: int = int(service_api_res[3][:3]) if len(service_api_res) >= 3 else None
                if status_code is not None and status_code < 400 or status_code == expected_code:
                    return service_api_res

                log.error(
                    f"service request fail, [%s]: %s, body:%s, params:%s, headers:%s, status_code:%s, msg:%s, \n response:%s",
                    method, url, body, params, headers, status_code, msg, service_api_res)
                if status_code is not None:

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
            except Exception as e:  # 這邊捕捉Server side err
                err = e.__str__()

                err_msg: str = (
                    f"unhandled {function_name} request error,\n"
                    f"url:{url}, \n"
                    f"params: {params}\n, "
                    f"headers: {headers}\n,"
                    f"error detail: {err} \n,"
                    )
                log.error(err_msg)
                raise ServerException(msg=err_msg)

        return wrapper_check_response_code

    return decorator_check_response_code
