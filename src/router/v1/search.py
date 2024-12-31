from typing import List, Dict, Any
from fastapi import (
    APIRouter,
    Request, Depends,
    Header, Path, Query, Body, Form
)
from ...domain.mentor.model import (
    mentor_model as mentor,
)
from ...domain.search.model import (
    search_model as search,
)
from ...app._di.injection import (
    _mentor_service,
    _search_service,
)
from ..res.response import *
from ...config.conf import *
from ...config.constant import *
from ...config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix='/mentors',
    tags=['Search Mentors'],
    responses={404: {'description': 'Not found'}},
)


# TODO: read from SEARCH service
@router.get('',
            responses=idempotent_response('mentor_list', search.SearchMentorProfileListVO))
async def mentor_list(
    search_patterns: List[str] = Query(None),
    filter_positions: List[str] = Query(None),
    filter_skills: List[str] = Query(None),
    filter_topics: List[str] = Query(None),
    filter_expertises: List[str] = Query(None),
    filter_industries: List[str] = Query(None),
    sorting_by: SortingBy = Query(SortingBy.UPDATED_TIME),
    sorting: Sorting = Query(Sorting.DESC),
    next_id: int = Query(None),
):
    # TODO: implement
    query = search.SearchMentorProfileDTO(
        search_patterns=search_patterns,
        filter_positions=filter_positions,
        filter_skills=filter_skills,
        filter_topics=filter_topics,
        filter_expertises=filter_expertises,
        filter_industries=filter_industries,
        sorting_by=sorting_by,
        sorting=sorting,
        next_id=next_id,
    )
    return res_success(data=None)


# TODO: read from professional service
@router.get('/{user_id}',
            responses=idempotent_response('get_mentor', mentor.MentorProfileVO))
async def get_mentor(
    user_id: int = Path(...),
):
    # TODO: implement
    return res_success(data=None)


# TODO: read from professional service
@router.get('/{user_id}/schedule',
            responses=idempotent_response('get_mentor_schedule', mentor.MentorScheduleVO))
async def get_mentor_schedule(
    user_id: int = Path(...),
    year: int = Query(SCHEDULE_YEAR),
    batch: int = Query(BATCH),
    next_id: int = Query(0),
):
    # TODO: implement
    return res_success(data=None)
