import logging
from typing import Optional, Dict, Any

from ..model.mentor_model import (
    MentorProfileDTO,
    MentorProfileVO,
    MentorScheduleVO,
    MentorScheduleQueryVO,
    MentorScheduleDTO,
)
from ....config.conf import USER_SERVICE_URL, DEFAULT_LANGUAGE, CACHE_TTL
from ....config.constant import MENTORS, Language
from ....config.exception import NotFoundException, raise_http_exception
from ....infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ....infra.template.cache import ICache
from ....infra.template.service_response import ServiceApiResponse

log = logging.getLogger(__name__)


class MentorService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache, local_cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache
        self.local_cache = local_cache

    async def get_mentor_profile(self, user_id: int, language: str = DEFAULT_LANGUAGE) -> MentorProfileVO:

        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/{language}/mentor_profile"

        res: Optional[Dict[str, Any]] = await self.service_api.simple_get(url=req_url)
        if not res:
            raise NotFoundException(msg='Mentor profile not found')
        return res

    async def upsert_mentor_profile(self, data: MentorProfileDTO) -> Optional[Dict[str, Any]]:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/mentor_profile"
        # SeniorityLevel 等 enum 需序列化為 JSON 可傳送值
        res: Optional[Dict[str, Any]] = await self.service_api.simple_put(
            url=req_url, json=data.model_dump(mode='json'),
        )
        return res

    def cache_key(self, category: str, language: str):
        return f"{category}:{language}"


    async def get_schedules(self, user_id: int, dt_year: int, dt_month: int, query: Optional[Dict] = None) -> MentorScheduleQueryVO:
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule/y/{dt_year}/m/{dt_month}'
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url, params=query)
        return MentorScheduleQueryVO(**res.data)


    async def save_schedules(self, user_id: int, data: MentorScheduleDTO) -> MentorScheduleVO:
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule'
        timeslots = [d.model_dump() for d in data.timeslots]
        req_json = {
            "until": data.until,
            "timeslots": timeslots,
        }
        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=req_json)
        return MentorScheduleVO(**res.data)


    async def delete_schedule(self, user_id: int, schedule_id: int) -> Optional[ServiceApiResponse]:
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule/{schedule_id}'
        res: Optional[ServiceApiResponse] = await self.service_api.delete(url=req_url)
        return res

