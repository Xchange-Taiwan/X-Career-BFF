import logging as log
from typing import Optional

from pydantic import UUID4

from src.app.template.service_response import ServiceApiResponse
from src.config.constant import MICRO_SERVICE_URL, USER_SERVICE_PREFIX, API_VERSION, FILE
from src.domain.cache import ICache
from src.domain.file.model.file_info_model import FileInfoVO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter

log.basicConfig(filemode='w', level=log.INFO)


class FileService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_file_by_id(self, user_id: int, file_id: str) -> FileInfoVO:
        req_url = MICRO_SERVICE_URL + USER_SERVICE_PREFIX + API_VERSION + FILE + '/' + str(user_id) + '/' + str(file_id)
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return FileInfoVO(**res.data)
