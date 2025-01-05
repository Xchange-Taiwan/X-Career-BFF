import logging as log
from typing import Optional, Dict, Any
from fastapi.encoders import jsonable_encoder

from src.infra.template.service_response import ServiceApiResponse
from src.config.conf import USER_SERVICE_URL, DEFAULT_LANGUAGE, CACHE_TTL
from src.config.constant import Language, InterestCategory, USERS
from src.config.exception import NotFoundException, raise_http_exception
from src.domain.user.model.common_model import InterestListVO, ProfessionListVO
from src.domain.user.model.user_model import ProfileDTO, ProfileVO
from src.domain.user.model.reservation_model import (
    ReservationQueryDTO, 
    UpdateReservationDTO, 
    ReservationDTO,
)
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from src.infra.template.cache import ICache

log.basicConfig(filemode='w', level=log.INFO)


class UserService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache, local_cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache
        self.local_cache = local_cache

    async def get_user_profile(self, user_id: int, language: str = DEFAULT_LANGUAGE) -> Optional[Dict[str, Any]]:
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
            cache_key = self.cache_key(f"interests:{interest.value}", language.value)
            cache_val = await self.local_cache.get(cache_key)
            if cache_val:
                return cache_val

            req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{language.value}/interests"
            res: Dict = await self.service_api.simple_get(url=req_url, params={'interest': interest.value})
            # set cache
            await self.local_cache.set(cache_key, res, CACHE_TTL)
            return res

        except Exception as e:
            log.error(e)
            raise_http_exception(e, 'Internal Server Error')

    async def get_industries(self, language: Language) -> Dict:
        try:
            cache_key = self.cache_key(f"professions:INDUSTRY", language.value)
            cache_val = await self.local_cache.get(cache_key)
            if cache_val:
                return cache_val
            
            req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{language.value}/industries"
            res: Dict = await self.service_api.simple_get(url=req_url)
            # set cache
            await self.local_cache.set(cache_key, res, CACHE_TTL)
            return res

        except Exception as e:
            log.error(e)
            raise_http_exception(e, 'Internal Server Error')

    def cache_key(self, category: str, language: str):
        return f"{category}:{language}"


    async def get_reservation_list(self, user_id: int, query: ReservationQueryDTO) -> Dict:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/reservations"
        res: Dict = await self.service_api.simple_get(url=req_url, params=query.model_dump())
        return res

    async def new_booking(self, body: ReservationDTO) -> Dict:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{body.my_user_id}/reservations"
        payload = jsonable_encoder(body)
        res: Dict = await self.service_api.simple_post(url=req_url, json=payload)
        return res

    async def update_reservation_status(self, reservation_id: int, body: UpdateReservationDTO) -> Dict:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/{body.my_user_id}/reservations/{reservation_id}"
        payload = jsonable_encoder(body)
        res: Dict = await self.service_api.simple_put(url=req_url, json=payload)
        return res
