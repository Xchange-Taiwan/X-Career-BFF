import logging as log
from typing import Optional

from src.domain.cache import ICache
from .model.experience_model import ExperienceVO, ExperienceDTO
from .model.mentor_model import MentorProfileDTO, MentorProfileVO
from ..user.model.common_model import ProfessionListVO
from ...app.template.service_response import ServiceApiResponse
from ...config.conf import USER_SERVICE_URL
from ...config.constant import USER_SERVICE_PREFIX, MENTORS, ExperienceCategory
from ...config.exception import NotFoundException
from ...infra.client.async_service_api_adapter import AsyncServiceApiAdapter

log.basicConfig(filemode='w', level=log.INFO)


class MentorService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_mentor_profile(self, user_id: int, language: str = 'CHT') -> MentorProfileVO:

        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/{user_id}/{language}/profile"

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

    async def get_expertises(self) -> ProfessionListVO:
        req_url = f"{USER_SERVICE_URL}/v1/{MENTORS}/expertises"
        res: Optional[ServiceApiResponse] = await self.service_api.get(url=req_url)
        return ProfessionListVO(**res.data)
