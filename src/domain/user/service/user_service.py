import logging as log
from typing import Optional, Dict

from src.app.template.service_response import ServiceApiResponse
from src.config.cache import gw_cache
from src.config.conf import USER_SERVICE_URL
from src.config.constant import Language, InterestCategory, USERS
from src.config.exception import raise_http_exception
from src.domain.cache import ICache
from src.domain.user.model.common_model import InterestListVO, ProfessionListVO
from src.domain.user.model.user_model import ProfileDTO, ProfileVO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter

log.basicConfig(filemode='w', level=log.INFO)


class UserService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_user_profile(self, user_id: int) -> ProfileVO:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/profile"
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return ProfileVO(**res.data)

    async def upsert_user_profile(self, user_id: int, data: ProfileDTO) -> ProfileVO:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/profile"
        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=data.dict())
        return ProfileVO(**res.data)

    async def get_interests(self, language: Language, interest: InterestCategory) -> InterestListVO:
        try:
            req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{language.value}/interests"
            res: Dict = await self.service_api.simple_get(url=req_url, params={'interest': interest.value})
            return res
        except Exception as e:
            log.error(e)
            raise_http_exception(500, 'Internal Server Error')

    async def get_industries(self, language: Language) -> ProfessionListVO:
        try:
            req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{language.value}/industries"
            res: Dict = await self.service_api.simple_get(url=req_url)
            return res
        except Exception as e:
            log.error(e)
            raise_http_exception(500, 'Internal Server Error')


user_service: UserService = UserService(AsyncServiceApiAdapter(), gw_cache)
