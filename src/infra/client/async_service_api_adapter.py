import functools
from typing import Dict, Optional
import functools
import logging
from typing import Dict, Optional

import httpx

from ...config.exception import *
from ...infra.template.service_api import IServiceApi
from ...infra.template.service_response import ServiceApiResponse

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


SUCCESS_CODE = "0"


def check_response_code(method: str, expected_code: int = 200):
    def decorator_check_response_code(func):

        @functools.wraps(func)
        async def wrapper_check_response_code(*args, **kwargs):
            # request params
            function_name: str = func.__name__
            url = kwargs.get('url', args[1] if len(args) > 1 else None)
            params = kwargs.get('params', args[2] if len(args) > 2 else None)
            body = kwargs.get('json', args[2] if len(args) > 2 else None)
            headers = kwargs.get('headers', args[3] if len(args) > 3 else None)
            
            # response params
            status_code: int = 0
            code: str = ''
            msg: str = ''
            data: Dict = None

            service_api_res: ServiceApiResponse = await func(*args, **kwargs)
            status_code = service_api_res.status_code
            if status_code is not None and (status_code < 400 or status_code == expected_code):
                return service_api_res

            res_body = service_api_res.res_json
            code = res_body.get('code', None)
            msg = res_body.get('msg', None)
            data = res_body.get('data', None)

            if status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
                msg = 'client input error (422: unprocessable client exception)'
                data = res_body.get('detail', [])

            log.error(
                f'service request fail,\n [%s]: %s;\n BODY: %s;\n PARAMS: %s;\n HEADERS: %s;\n \
                STATUS_CODE: %s;\n RESP_BODY: %s;\n ERR_MSG: %s;\n  DATA/422_DETAIL: %s\n',
                method, url, body, params, headers, 
                status_code, res_body, msg, data)
            raise_http_exception_by_status_code(status_code, msg, data)


        return wrapper_check_response_code

    return decorator_check_response_code


class AsyncServiceApiAdapter(IServiceApi):

    """
    return response body only
    """
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response: ServiceApiResponse = await self.get(url, params, headers)
        if service_api_response:
            return service_api_response.data
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
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"simple_get request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                      url, params, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)

        return result
    
    # NOTE: retrun native response
    async def get_req(self, url: str, params: Dict = None, headers: Dict = None) -> Any:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"get_req request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                      url, params, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)

    """
    return response body only
    """
    async def simple_post(self, url: str, json: Dict, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response: ServiceApiResponse = await self.post(url, json, headers)
        if service_api_response:
            return service_api_response.data
        return None

    @check_response_code('post', 201)
    async def post(self, url: str, json: Dict, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=json, headers=headers)
                result = ServiceApiResponse.parse(response)

        except Exception as e:
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"simple_post request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                      url, json, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)

        return result

    # NOTE: retrun native response
    async def post_req(self, url: str, json: Dict, headers: Dict = None) -> Any:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=json, headers=headers)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"post_req request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                      url, json, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)

    """
    return response body only
    """
    async def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response: ServiceApiResponse = await self.put(url, json, headers)
        if service_api_response:
            return service_api_response.data
        return None

    @check_response_code('put', 200)
    async def put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=json, headers=headers)
                result = ServiceApiResponse.parse(response)

        except Exception as e:
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"simple_put request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                      url, json, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)

        return result

    """
    return response body only
    """
    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        service_api_response = await self.delete(url, params, headers)
        if service_api_response:
            return service_api_response.data
        return None

    @check_response_code('delete', 200)
    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, params=params, headers=headers)
                result = ServiceApiResponse.parse(response)

        except Exception as e:
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"simple_delete request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                      url, params, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)

        return result
