from typing import List
from fastapi import (
    APIRouter,
    Path, Body
)
from httpx import Response

from ...domain.mentor.mentor_service import MentorService
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ...domain.mentor.model import (
    mentor_model as mentor,
    experience_model as experience,
)
from ...domain.user.model import (
    common_model as common,
)
from ..res.response import *
from ...config.constant import *
from ...config.exception import *
import logging as log
import httpx

log.basicConfig(filemode='w', level=log.INFO)

router = APIRouter(
    prefix='/mentors',
    tags=['Mentor'],
    responses={404: {'description': 'Not found'}},
)
_mentor_service = MentorService(
    AsyncServiceApiAdapter(),
    None
)
# Resquest obj is used to access router path
@router.put('/{user_id}/profile',
            responses=idempotent_response('upsert_mentor_profile', mentor.MentorProfileVO))
async def upsert_mentor_profile(
        request: Request,
        user_id: int = Path(...),
        body: mentor.MentorProfileDTO = Body(...),
):
    router_path = request.url.path
    res: mentor.MentorProfileVO = None
    req_url = MICRO_SERVICE_URL + router_path
    async with httpx.AsyncClient() as client:
        res = await client.get(req_url)
    return res_success(data=res)


@router.get('/{user_id}/profile',
            responses=idempotent_response('get_mentor_profile', mentor.MentorProfileVO))
async def get_mentor_profile(
        request: Request,
        user_id: int = Path(...),
):
    return await _mentor_service.get_mentor_profile(user_id)


@router.put('/{user_id}/experiences/{experience_type}',
            responses=idempotent_response('upsert_experience', experience.ExperienceVO))
async def upsert_experience(
        user_id: int = Path(...),
        experience_type: ExperienceCategory = Path(...),
        body: experience.ExperienceDTO = Body(...),
):
    # TODO: implement
    return res_success(data=None)


@router.delete('/{user_id}/experiences/{experience_type}/{experience_id}',
               responses=idempotent_response('delete_experience', experience.ExperienceVO))
async def delete_experience(
        user_id: int = Path(...),
        experience_id: int = Path(...),
        experience_type: ExperienceCategory = Path(...),
):
    # TODO: implement
    return res_success(data=None)


@router.get('/expertises',
            responses=idempotent_response('get_expertises', common.ProfessionListVO))
async def get_expertises(
        # category = ProfessionCategory.EXPERTISE = Query(...),
):
    # TODO: implement
    return res_success(data=None)


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
