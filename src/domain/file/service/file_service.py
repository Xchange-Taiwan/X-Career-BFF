import logging as log
from typing import Optional, List

from pydantic import UUID4

from src.app.template.service_response import ServiceApiResponse
from src.config.cache import gw_cache
from src.config.constant import MICRO_SERVICE_URL, USER_SERVICE_PREFIX, API_VERSION, FILE
from src.domain.cache import ICache
from src.domain.file.model.file_info_model import FileInfoVO, FileInfoDTO, FileInfoListVO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter

log.basicConfig(filemode='w', level=log.INFO)


class FileService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache
        self.file_url = MICRO_SERVICE_URL + USER_SERVICE_PREFIX + API_VERSION + FILE

    async def get_file_by_id(self, user_id: int, file_id: str) -> FileInfoVO:
        req_url = self.file_url + '/' + str(user_id) + '/' + str(file_id)
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return FileInfoVO(**res.data)

    async def get_file_info_by_user_id(self, user_id: int) -> FileInfoListVO:
        req_url = self.file_url + '/' + str(user_id)
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return FileInfoListVO(**res.data)

    async def create_file_info(self, file_info_dto: FileInfoDTO) -> FileInfoVO:
        req_url = self.file_url + '/' + 'create'
        res: Optional[ServiceApiResponse] = await self.service_api.post(url=req_url, json=file_info_dto.dict())
        return FileInfoVO(**res.data)

    async def update_file_info(self, user_id: int, file_info_dto: FileInfoDTO) -> FileInfoVO:
        req_url = self.file_url + '/' + str(user_id) + '/' + 'update'
        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=file_info_dto.dict())
        return FileInfoVO(**res.data)

    async def delete_file_info(self, user_id: int, file_id: str) -> bool:
        req_url = self.file_url + '/' + str(user_id) + '/' + file_id
        res: Optional[ServiceApiResponse] = await self.service_api.delete(url=req_url)
        return res.data


file_service_singleton = FileService(
    AsyncServiceApiAdapter(),
    gw_cache
)
