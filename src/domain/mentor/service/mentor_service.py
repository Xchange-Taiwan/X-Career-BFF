import logging as log
from typing import List, Optional, Dict, Any

from ..model.experience_model import ExperienceVO, ExperienceDTO
from ..model.mentor_model import (
    MentorProfileDTO, 
    MentorProfileVO,
    MentorScheduleVO,
    MentorScheduleDTO,
)
from ...user.model.common_model import ProfessionListVO
from ....config.conf import USER_SERVICE_URL
from ....config.constant import MENTORS, ExperienceCategory, Language
from ....config.exception import NotFoundException, raise_http_exception
from ....infra.template.service_response import ServiceApiResponse
from ....infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ....infra.template.cache import ICache

log.basicConfig(filemode='w', level=log.INFO)


class MentorService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_mentor_profile(self, user_id: int, language: str = 'zh_TW') -> MentorProfileVO:

        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/{language}/mentor_profile"

        res: Optional[Dict[str, Any]] = await self.service_api.simple_get(url=req_url)
        if not res:
            raise NotFoundException(msg='Mentor profile not found')
        return res

    async def upsert_mentor_profile(self, data: MentorProfileDTO) -> Optional[Dict[str, Any]]:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/mentor_profile"
        res: Optional[Dict[str, Any]] = await self.service_api.simple_put(url=req_url, json=data.model_dump())
        return res

    async def upsert_experience(self, data: ExperienceDTO, user_id: int, experience_type: str) -> ExperienceVO:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/experiences/{experience_type}"

        res: Optional[ServiceApiResponse] = await self.service_api.put(url=req_url, json=data.model_dump())
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
        req_url = f'{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/schedule/y/{dt_year}/m/{dt_month}'
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url, params=query)
        return MentorScheduleVO(**res.data)


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
