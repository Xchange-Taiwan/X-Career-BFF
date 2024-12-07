from typing import List

from fastapi import (
    APIRouter,
    Path, Body
)

from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ..res.response import *
from ...config.cache import gw_cache
from ...config.constant import ExperienceCategory, Language
from ...config.exception import *
from ...domain.mentor.mentor_service import MentorService
from ...domain.mentor.model import (
    mentor_model as mentor,
    experience_model as experience,
)
from ...domain.user.model import (
    common_model as common,
)

log.basicConfig(filemode='w', level=log.INFO)

router = APIRouter(
    prefix='/mentors',
    tags=['Mentor'],
    responses={404: {'description': 'Not found'}},
)
_mentor_service = MentorService(
    AsyncServiceApiAdapter(),
    gw_cache
)


# Resquest obj is used to access router path
@router.put('/{user_id}/profile',
            responses=idempotent_response('upsert_mentor_profile', mentor.MentorProfileVO))
async def upsert_mentor_profile(
        request: Request,
        user_id: int = Path(...),
        body: mentor.MentorProfileDTO = Body(...),
):
    if user_id != body.user_id:
        raise ForbiddenException(msg='user_id not match')
    res: mentor.MentorProfileVO = await _mentor_service.upsert_mentor_profile(body)
    return res_success(data=res)


@router.get('/{user_id}/{language}/profile',
            responses=idempotent_response('get_mentor_profile', mentor.MentorProfileVO))
async def get_mentor_profile(
        # request: Request,
        user_id: int = Path(...),
        language: str = Path(...),
):
    return await _mentor_service.get_mentor_profile(user_id, language)


@router.put('/{user_id}/experiences/{experience_type}',
            responses=idempotent_response('upsert_experience', experience.ExperienceVO))
async def upsert_experience(
        user_id: int = Path(...),
        experience_type: ExperienceCategory = Path(...),
        body: experience.ExperienceDTO = Body(...),
):

    res: experience.ExperienceVO = await _mentor_service.upsert_experience(body, user_id, experience_type.value)
    return res_success(data=res.json())


@router.delete('/{user_id}/experiences/{experience_type}/{experience_id}',
               responses=idempotent_response('delete_experience', experience.ExperienceVO))
async def delete_experience(
        user_id: int = Path(...),
        experience_id: int = Path(...),
        experience_type: ExperienceCategory = Path(...),
):

    res: bool = await _mentor_service.delete_experience(user_id, experience_id, experience_type.value)
    return res_success(data=res)


@router.get('/{language}/expertises',
            responses=idempotent_response('get_expertises', common.ProfessionListVO))
async def get_expertises(
        language: Language = Path(...)
        # can't use a certain enum as query, need to be a type
         # category : ProfessionCategory.EXPERTISE = Query(...),
):
    res: Dict = await _mentor_service.get_expertises(language)
    return res_success(data=res)


@router.put('/{user_id}/schedule',
            responses=idempotent_response('upsert_mentor_schedule', mentor.MentorScheduleVO))
async def upsert_mentor_schedule(
        user_id: int = Path(...),
        body: List[mentor.TimeSlotDTO] = Body(...),
):
    # TODO: implement
    return res_success(data=None)


@router.delete('/{user_id}/schedule/{schedule_id}',
               responses=idempotent_response('delete_mentor_schedule', mentor.MentorScheduleVO))
async def delete_mentor_schedule(
        user_id: int = Path(...),
        schedule_id: int = Path(...),
):
    # TODO: implement
    return res_success(data=None)
