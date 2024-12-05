from typing import Optional

from src.app.template.service_response import ServiceApiResponse
from src.config.cache import gw_cache
from src.config.conf import USER_SERVICE_URL
from src.config.constant import ProfessionCategory, \
    InterestCategory, USERS
from src.domain.cache import ICache
from src.domain.user.model.common_model import InterestListVO, ProfessionListVO
from src.domain.user.model.user_model import ProfileDTO, ProfileVO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter


class UserService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_user_profile(self, user_id: int):
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/profile"
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return ProfileVO(**res.data)

    async def upsert_user_profile(self, user_id: int, data: ProfileDTO):
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/profile"
        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=data.dict())
        return ProfileVO(**res.data)

    async def get_interests(self, interest: InterestCategory) -> InterestListVO:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/interests"
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url, params={'interest': interest.value})
        return InterestListVO(**res.data)

    async def get_industries(self, profession_category: ProfessionCategory) -> ProfessionListVO:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/industries"
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url, params={'category': profession_category.value})
        return ProfessionListVO(**res.data)


user_service_singleton: UserService = (
    UserService(
        AsyncServiceApiAdapter(),
        gw_cache))
