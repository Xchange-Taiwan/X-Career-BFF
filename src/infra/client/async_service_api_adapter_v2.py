import functools
from fastapi import status
from typing import Dict, Optional
import httpx
from ...app.template.service_response import ServiceApiResponse
from ...app.template.service_api import IServiceApi
from ...config.exception import *
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


SUCCESS_CODE = "0"


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
                status_code: int = int(service_api_res[3][:3]) if len(
                    service_api_res) >= 3 else None
                if status_code is not None and (status_code < 400 or status_code == expected_code):
                    return service_api_res

                log.error(
                    f"service request fail, [%s]: %s, body:%s, params:%s, headers:%s, status_code:%s, msg:%s, err: %s \n response:%s",
                    method, url, body, params, headers, status_code, msg, err, service_api_res)
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


class AsyncServiceApiAdapterV2(IServiceApi):

    """
    return response body only
    """
    @check_response_code('get', 200)
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response = await self.get(url, params, headers)
        if service_api_response:
            return service_api_response.get_data()
        return None

    @check_response_code('get', 200)
    async def get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                result = ServiceApiResponse.parse(response)

        except Exception as e:
            log.error(f"simple_get request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                      url, params, headers, response, e.__str__())
            raise ServerException(msg='get_connection_error')

        return result

    """
    return response body only
    """
    @check_response_code('post', 201)
    async def simple_post(self, url: str, json: Dict, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response = await self.post(url, json, headers)
        if service_api_response:
            return service_api_response.get_data()
        return None

    @check_response_code('post', 201)
    async def post(self, url: str, json: Dict, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=json, headers=headers)
                result = response.json()

        except Exception as e:
            log.error(f"simple_post request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                      url, json, headers, response, e.__str__())
            raise ServerException(msg='post_connection_error')

        return result

    """
    return response body only
    """
    @check_response_code('put', 200)
    async def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response = await self.put(url, json, headers)
        if service_api_response:
            return service_api_response.get_data()
        return None

    @check_response_code('put', 200)
    async def put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=json, headers=headers)
                result = response.json()

        except Exception as e:
            log.error(f"simple_put request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                      url, json, headers, response, e.__str__())
            raise ServerException(msg='put_connection_error')

        return result

    """
    return response body only
    """
    @check_response_code('delete', 200)
    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response = await self.delete(url, params, headers)
        if service_api_response:
            return service_api_response.get_data()
        return None

    @check_response_code('delete', 200)
    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, params=params, headers=headers)
                result = response.json()

        except Exception as e:
            log.error(f"simple_delete request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                      url, params, headers, response, e.__str__())
            raise ServerException(msg='delete_connection_error')

        return result
