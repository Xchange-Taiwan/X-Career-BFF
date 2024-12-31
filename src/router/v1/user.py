import os
import time
import json
from typing import List, Dict, Any
from fastapi import (
    APIRouter,
    Request, Depends,
    Header, Path, Query, Body, Form
)
from fastapi.encoders import jsonable_encoder

from ...domain.user.model import (
    common_model as common,
    user_model as user,
    reservation_model as reservation,
)
from ..res.response import *
from ...config.constant import *
from ...config.exception import *
import logging as log

from ...domain.user.model.common_model import InterestListVO
from ...app._di.injection import _user_service

log.basicConfig(filemode='w', level=log.INFO)

router = APIRouter(
    prefix='/users',
    tags=['User'],
    responses={404: {'description': 'Not found'}},
)


@router.put('/{user_id}/profile',
            responses=idempotent_response('upsert_profile', user.ProfileVO))
async def upsert_profile(
        user_id: int = Path(...),
        body: user.ProfileDTO = Body(...),
):
    # user_id 在此 API 可省略，但因為給前端的 API swagger doc 已固定，所以保留
    if user_id != body.user_id:
        raise ForbiddenException(msg='user_id not match')
    data = await _user_service.upsert_user_profile(body)
    return res_success(data=data)


@router.get('/{user_id}/{language}/profile',
            responses=idempotent_response('get_profile', user.ProfileVO))
async def get_profile(
        user_id: int = Path(...),
        language: Language = Path(...),
):
    data: user.ProfileVO = await _user_service.get_user_profile(user_id, language.value)
    return res_success(data=jsonable_encoder(data))


@router.get('/{language}/interests',
            responses=idempotent_response('get_interests', common.InterestListVO))
async def get_interests(
        language: Language = Path(...),
        interest: InterestCategory = Query(...),
):
    data: Dict = await _user_service.get_interests(language, interest)
    return res_success(data=jsonable_encoder(data))


@router.get('/{language}/industries',
            responses=idempotent_response('get_industries', common.ProfessionListVO))
async def get_industries(
        language: Language = Path(...)
):
    data: Dict = await _user_service.get_industries(language)
    return res_success(data=jsonable_encoder(data))


@router.get('/{user_id}/reservations',
            responses=idempotent_response('reservation_list', reservation.ReservationListVO))
async def reservation_list(
        user_id: int = Path(...),
        state: ReservationListState = Query(...),
        batch: int = Query(...),
        next_id: int = Query(None),
):
    # TODO: implement
    return res_success(data=None)


@router.post('/{user_id}/reservations',
             responses=post_response('new_booking', reservation.ReservationVO))
async def new_booking(
        user_id: int = Path(...),
        body: reservation.ReservationDTO = Body(...),
):
    # TODO: implement
    return res_success(data=None)


@router.put('/{user_id}/reservations/{reservation_id}',
            responses=idempotent_response('update_or_delete_booking', reservation.ReservationVO))
async def update_or_delete_booking(
        user_id: int = Path(...),
        reservation_id: int = Path(...),
        body: reservation.ReservationDTO = Body(...),
):
    # TODO: implement
    return res_success(data=None)
