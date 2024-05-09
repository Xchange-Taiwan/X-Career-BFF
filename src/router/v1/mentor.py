import logging as log
from typing import List

from fastapi import (
    APIRouter,
    Path, Body, Depends
)
from sqlalchemy.orm import Session

from ..res.response import *
from ...config.constant import *
from src.domain.mentor.service.mentor_service import MentorService
from ...domain.mentor.model import (
    mentor_model as mentor,
    experience_model as experience,
)
from ...domain.user.model import (
    common_model as common,
)
from ...infra.databse import get_db
from ...infra.util.injection_util import get_mentor_service

log.basicConfig(filemode='w', level=log.INFO)

router = APIRouter(
    prefix='/mentors',
    tags=['Mentor'],
    responses={404: {'description': 'Not found'}},
)


@router.put('/mentor_profile/create',
            responses=idempotent_response('upsert_mentor_profile', mentor.MentorProfileVO))
async def upsert_mentor_profile(
        body: mentor.MentorProfileDTO = Body(...),
        mentor_service: MentorService = Depends(get_mentor_service),
        db: Session = Depends(get_db)
):
    # TODO: implement
    res: mentor.MentorProfileVO = await mentor_service.upsert_mentor_profile(body, db)
    return res_success(data=res.json())


@router.get('/{user_id}/profile',
            responses=idempotent_response('get_mentor_profile', mentor.MentorProfileVO))
async def get_mentor_profile(
        user_id: int = Path(...),
        db: Session = Depends(get_db)
):
    # TODO: implement

    # profile = mentor_service.get_

    return res_success(data=None)


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
