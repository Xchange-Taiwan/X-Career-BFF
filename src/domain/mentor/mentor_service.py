import logging as log
from typing import Optional, Dict, List

from src.domain.cache import ICache
from .model.experience_model import ExperienceVO, ExperienceDTO
from .model.mentor_model import (
    MentorProfileDTO, 
    MentorProfileVO,
    MentorScheduleVO,
    TimeSlotDTO,
)
from ..user.model.common_model import ProfessionListVO
from ...app.template.service_response import ServiceApiResponse
from ...config.conf import USER_SERVICE_URL
from ...config.constant import MENTORS, ExperienceCategory, Language
from ...config.exception import NotFoundException, raise_http_exception
from ...config.cache import gw_cache
from ...config.service_client import (
    AsyncServiceApiAdapter,
    service_client,
)

log.basicConfig(filemode='w', level=log.INFO)


class MentorService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_mentor_profile(self, user_id: int, language: str = 'zh_TW') -> MentorProfileVO:

        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/{language}/mentor_profile"

        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        if not res:
            raise NotFoundException(msg='Mentor profile not found')
        return MentorProfileVO(**res.data)

    async def upsert_mentor_profile(self, data: MentorProfileDTO) -> MentorProfileVO:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/mentor_profile/create"

        res: Optional[ServiceApiResponse] = await self.service_api.post(url=req_url, json=data.dict())
        return MentorProfileVO(**res.data)

    async def upsert_experience(self, data: ExperienceDTO, user_id: int, experience_type: str) -> ExperienceVO:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/experiences/{experience_type}"

        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=data.dict())
        res_data = res.data

        return ExperienceVO.of(res_data.get('id'),
                               res_data.get('desc'),
                               res_data.get('order'),
                               ExperienceCategory(res_data.get('category')))

    async def delete_experience(self, user_id: int, exp_id: int, exp_cate: str) -> bool:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/experiences/{exp_cate}/{exp_id}"

        res: Optional[ServiceApiResponse] = await self.service_api.delete(url=req_url)
        return res.data

    async def get_expertises(self, language: Language) -> ProfessionListVO:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{language.value}/expertises"
        res: Dict = await self.service_api.simple_get(url=req_url)
        return res


    async def get_schedules(self, user_id: int, dt_year: int, dt_month: int, query: Optional[Dict] = None) -> MentorScheduleVO:
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule/{dt_year}/{dt_month}'
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url, params=query)
        return MentorScheduleVO(**res.data)


    async def save_schedules(self, user_id: int, data: List[TimeSlotDTO]) -> MentorScheduleVO:
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule'
        req_json = [d.dict() for d in data]
        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=req_json)
        return MentorScheduleVO(**res.data)


    async def delete_schedule(self, user_id: int, schedule_id: int) -> Optional[ServiceApiResponse]:
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule/{schedule_id}'
        res: Optional[ServiceApiResponse] = await self.service_api.delete(url=req_url)
        return res

_mentor_service = MentorService(
    service_client,
    gw_cache
)
