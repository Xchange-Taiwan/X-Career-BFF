import logging
from typing import Optional, Dict, Any

from fastapi.encoders import jsonable_encoder

from src.config.conf import USER_SERVICE_URL, DEFAULT_LANGUAGE
from src.config.constant import USERS
from src.config.exception import NotFoundException
from src.domain.user.model.reservation_model import (
    ReservationQueryDTO,
    UpdateReservationDTO,
    ReservationDTO,
)
from src.domain.user.model.user_model import ProfileDTO
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from src.infra.template.cache import ICache

log = logging.getLogger(__name__)


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

    async def upsert_user_profile(self, data: ProfileDTO) -> Optional[Dict[str, Any]]:
        req_url = f"{USER_SERVICE_URL}/v1/{USERS}/profile"
        res: Optional[Dict[str, Any]] = await self.service_api.simple_put(url=req_url, json=data.model_dump())
        return res

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
