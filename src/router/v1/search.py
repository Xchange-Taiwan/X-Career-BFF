import logging as log
from datetime import datetime
from typing import List

from fastapi import (
    APIRouter,
    Path, Query
)

from ..res.response import *
from ...app._di.injection import (
    _mentor_service,
    _search_service,
)
from ...domain.mentor.model import (
    mentor_model as mentor,
)
from ...domain.search.model import (
    search_model as search,
)

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix='/mentors',
    tags=['Search Mentors'],
    responses={404: {'description': 'Not found'}},
)


@router.get('',
            responses=idempotent_response('mentor_list', search.SearchMentorProfileListVO))
async def mentor_list(
    search_pattern: str = Query(None),
    filter_positions: List[str] = Query(None),
    filter_skills: List[str] = Query(None),
    filter_topics: List[str] = Query(None),
    filter_expertises: List[str] = Query(None),
    filter_industries: List[str] = Query(None),
    limit: int = Query(9),
    cursor: datetime = Query(None),
):
    query = search.SearchMentorProfileDTO(
        search_pattern=search_pattern,
        filter_positions=filter_positions,
        filter_skills=filter_skills,
        filter_topics=filter_topics,
        filter_expertises=filter_expertises,
        filter_industries=filter_industries,
        limit=limit,
        cursor=cursor,
    )
    data = await _search_service.search_mentor(query=query)
    return res_success(data)


# TODO: read from professional service
@router.get('/{user_id}',
            responses=idempotent_response('get_mentor', mentor.MentorProfileVO))
async def get_mentor(
    user_id: int = Path(...),
):
    # TODO: implement
    return res_success(data=None)


@router.get('/{user_id}/schedule/y/{dt_year}/m/{dt_month}',
            responses=idempotent_response('get_mentor_schedule_list', mentor.MentorScheduleVO))
async def get_schedules(
        user_id: int = Path(...),
        dt_year: int = Path(...),
        dt_month: int = Path(...),
        limit: int = Query(None, ge=1),
        next_dtstart: int = Query(None),
):
    query = None
    if limit:
        query = {'limit': limit, 'next_dtstart': next_dtstart or 0} # next_dtstart is optional

    res: mentor.MentorScheduleVO = await _mentor_service.get_schedules(
        user_id=user_id,
        dt_year=dt_year,
        dt_month=dt_month,
        query=query,
    )
    return res_success(data=res.model_dump())
