from typing import Optional

from src.app.template.service_response import ServiceApiResponse
from src.config.cache import gw_cache
from src.config.constant import MICRO_SERVICE_URL, USER_SERVICE_PREFIX, API_VERSION, USERS
from src.domain.cache import ICache
from src.domain.user.model.user_model import ProfileDTO, ProfileVO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter


class UserService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache
        self.url = MICRO_SERVICE_URL + USER_SERVICE_PREFIX + API_VERSION + USERS

    async def get_user_profile(self, user_id: int):
        req_url = self.url + '/' + str(user_id) + '/' + 'profile'
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return ProfileVO(**res.data)

    async def upsert_user_profile(self, user_id: int, data: ProfileDTO):
        req_url = self.url + '/' + str(user_id) + '/' + 'profile'
        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=data.dict())
        return ProfileVO(**res.data)


user_service_singleton: UserService = (
    UserService(
        AsyncServiceApiAdapter(),
        gw_cache))
