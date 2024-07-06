from typing import Optional, Dict

import httpx
from httpx import Response
from starlette.responses import JSONResponse

from src.domain.service_api import IServiceApi


class ServiceApiAdapter(IServiceApi):
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        # 單純給service回的data
        async with httpx.AsyncClient() as client:
            response: Response = await client.get(url=url, headers=headers)

            dto: Dict = response.json()
            return dto.get("data")  # 這裡應該是對應service的VO/responseDTO

    async def get(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.get(url=url, headers=headers)

            dto: Dict = response.json()
            server_res: JSONResponse = JSONResponse(content={
                'msg': dto.get("msg"),
                'data': dto.get("data")
            })

            return server_res  # 這裡應該是對應service的VO/responseDTO+msg

    async def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.get(url=url, headers=headers)
            # 直接回傳服務的Response
            return response.json()

    async def simple_post(self, url: str, json: Dict, headers: Dict = None) -> (Optional[Dict[str, str]]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.post(url=url, json=json, headers=headers)
            dto: Dict = response.json()
            return dto.get("data")  # 這裡應該是對應service的VO/responseDTO

    async def post_data(self, url: str, byte_data: bytes, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass

    async def post(self, url: str, json: Dict, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.post(url=url, json=json, headers=headers)
            dto: Dict = response.json()
            server_res: JSONResponse = JSONResponse(content={
                'msg': dto.get("msg"),
                'data': dto.get("data")
            })

            return server_res  # 這裡應該是對應service的VO/responseDTO+msg

    async def post_with_statuscode(self, url: str, json: Dict, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.post(url=url, json=json, headers=headers)
            # 直接回傳服務的Response
            return response.json()

    async def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.post(url=url, json=json, headers=headers)
            dto: Dict = response.json()
            return dto.get("data")  # 這裡應該是對應service的VO/responseDTO

    async def put(self, url: str, json: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.put(url=url, json=json, headers=headers)
            dto: Dict = response.json()
            server_res: JSONResponse = JSONResponse(content={
                'msg': dto.get("msg"),
                'data': dto.get("data")
            })

            return server_res  # 這裡應該是對應service的VO/responseDTO+msg

    async def put_with_statuscode(self, url: str, json: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.put(url=url, json=json, headers=headers)
            # 直接回傳服務的Response
            return response.json()

    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.delete(url=url, headers=headers)
            dto: Dict = response.json()
            return dto.get("data")  # 這裡應該是對應service的VO/responseDTO

    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.delete(url=url, headers=headers)
            dto: Dict = response.json()
            server_res: JSONResponse = JSONResponse(content={
                'msg': dto.get("msg"),
                'data': dto.get("data")
            })

            return server_res  # 這裡應該是對應service的VO/responseDTO+msg

    async def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (
            Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        async with httpx.AsyncClient() as client:
            response: Response = await client.delete(url=url, headers=headers)
            # 直接回傳服務的Response
            return response.json()
