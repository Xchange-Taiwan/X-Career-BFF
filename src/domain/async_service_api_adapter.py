import functools
import logging as log
from typing import Optional, Dict

import httpx
from httpx import Response
from starlette import status

from src.config.exception import ClientException, ForbiddenException, UnauthorizedException, NotFoundException, \
    NotAcceptableException, ServerException
from src.domain.service_api import IServiceApi


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
                # ex: 40400 取至404
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


class AsyncServiceApiAdapter(IServiceApi):
    @check_response_code('get', 200)
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        # 單純給service回的data
        async with httpx.AsyncClient() as client:
            response: Response = await client.get(url=url, headers=headers)

            dto: Dict = response.json()

            return dto.get('data')  # 直接回傳數據內容

    @check_response_code('get', 200)
    async def get(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''

        async with httpx.AsyncClient() as client:
            response: Response = await client.get(url=url, headers=headers)

            dto: Dict = response.json()
            msg: str = dto.get('msg')

            return dto.get('data'), msg, err  # 這裡應該是對應service的VO/responseDTO+msg

    @check_response_code('get', 200)
    async def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''
        code: Optional[int] = None
        try:
            async with httpx.AsyncClient() as client:
                response: Response = await client.get(url=url, headers=headers)

                dto: Dict = response.json()
                msg: Optional[str] = dto.get('msg', None)
                code: Optional[int] = dto.get('code', None)
        except Exception as e:
            err = e.__str__()

        return dto.get('data'), msg, err, code  # 這裡應該是對應service的VO/responseDTO+msg

    @check_response_code('post', 200)
    async def simple_post(self, url: str, data: Dict = None, headers: Dict = None) -> Optional[Dict[str, str]]:
        async with httpx.AsyncClient() as client:
            response: Response = await client.post(url=url, json=data, headers=headers)

            dto: Dict = response.json()

            return dto.get('data')

    @check_response_code('post', 200)
    async def post(self, url: str, data: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''

        async with httpx.AsyncClient() as client:
            response: Response = await client.post(url=url, json=data, headers=headers)

            dto: Dict = response.json()
            msg: str = dto.get('msg')

            return dto.get('data'), msg, err

    @check_response_code('post', 200)
    async def post_with_statuscode(self, url: str, data: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''
        code: Optional[int] = None
        try:
            async with httpx.AsyncClient() as client:
                response: Response = await client.post(url=url, json=data, headers=headers)

                dto: Dict = response.json()
                msg: Optional[str] = dto.get('msg', None)
                code: Optional[int] = dto.get('code', None)
        except Exception as e:
            err = e.__str__()

        return dto.get('data'), msg, err, code

    @check_response_code('post', 200)
    async def post_data(self, url: str, byte_data: bytes, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass

    @check_response_code('put', 200)
    async def simple_put(self, url: str, data: Dict = None, headers: Dict = None) -> Optional[Dict[str, str]]:
        async with httpx.AsyncClient() as client:
            response: Response = await client.put(url=url, json=data, headers=headers)

            dto: Dict = response.json()

            return dto.get('data')

    @check_response_code('put', 200)
    async def put(self, url: str, data: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''

        async with httpx.AsyncClient() as client:
            response: Response = await client.put(url=url, json=data, headers=headers)

            dto: Dict = response.json()
            msg: str = dto.get('msg')

            return dto.get('data'), msg, err

    @check_response_code('put', 200)
    async def put_with_statuscode(self, url: str, data: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''
        code: Optional[int] = None
        try:
            async with httpx.AsyncClient() as client:
                response: Response = await client.put(url=url, json=data, headers=headers)

                dto: Dict = response.json()
                msg: Optional[str] = dto.get('msg', None)
                code: Optional[int] = dto.get('code', None)
        except Exception as e:
            err = e.__str__()

        return dto.get('data'), msg, err, code

    @check_response_code('delete', 200)
    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, str]]:
        async with httpx.AsyncClient() as client:
            response: Response = await client.delete(url=url, headers=headers, params=params)

            dto: Dict = response.json()

            return dto.get('data')

    @check_response_code('delete', 200)
    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''

        async with httpx.AsyncClient() as client:
            response: Response = await client.delete(url=url, headers=headers, params=params)

            dto: Dict = response.json()
            msg: str = dto.get('msg')

            return dto.get('data'), msg, err

    @check_response_code('delete', 200)
    async def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        dto: Dict = {}  # init with empty dict
        msg: str = ''
        err: str = ''
        code: Optional[int] = None
        try:
            async with httpx.AsyncClient() as client:
                response: Response = await client.delete(url=url, headers=headers, params=params)

                dto: Dict = response.json()
                msg: Optional[str] = dto.get('msg', None)
                code: Optional[int] = dto.get('code', None)
        except Exception as e:
            err = e.__str__()

        return dto.get('data'), msg, err, code
