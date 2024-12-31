import logging as log
from typing import Optional, Dict, Any

from src.infra.template.service_response import ServiceApiResponse
from src.config.conf import USER_SERVICE_URL
from src.config.constant import Language, InterestCategory, USERS
from src.config.exception import NotFoundException, raise_http_exception
from src.domain.user.model.common_model import InterestListVO, ProfessionListVO
from src.domain.user.model.user_model import ProfileDTO, ProfileVO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from src.infra.template.cache import ICache

log.basicConfig(filemode='w', level=log.INFO)


class UserService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_user_profile(self, user_id: int, language: str = 'zh_TW') -> ProfileVO:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/{language}/profile"
        res: Optional[Dict[str, Any]] = await self.service_api.simple_get(url=req_url)
        if not res:
            raise NotFoundException(msg='Profile not found')
        return res

    async def upsert_user_profile(self, data: ProfileDTO) -> ProfileVO:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/profile"
        res: Optional[Dict[str, Any]] = await self.service_api.simple_put(url=req_url, json=data.model_dump())
        return res

    async def get_interests(self, language: Language, interest: InterestCategory) -> Dict:
        try:
            req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{language.value}/interests"
            res: Dict = await self.service_api.simple_get(url=req_url, params={'interest': interest.value})
            return res
        except Exception as e:
            log.error(e)
            raise_http_exception(e, 'Internal Server Error')

    async def get_industries(self, language: Language) -> Dict:
        try:
            req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{language.value}/industries"
            res: Dict = await self.service_api.simple_get(url=req_url)
            return res
        except Exception as e:
            log.error(e)
            raise_http_exception(e, 'Internal Server Error')
