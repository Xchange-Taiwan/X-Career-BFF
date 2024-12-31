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
    data: user.ProfileVO = await _user_service.upsert_user_profile(body)
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
            responses=idempotent_response('reservation_list', reservation.ReservationInfoListVO))
async def reservation_list(
        user_id: int = Path(...),
        query: reservation.ReservationQueryDTO = Query(...),
):
    res: Dict = await _user_service.get_reservation_list(user_id, query)
    return res_success(data=res)


############################################################################################
# NOTE: 如何改預約時段? 重新建立後再 cancel 舊的。 (status_code: 201)
# 用戶可能有很多memtor/memtee預約；為方便檢查時間衝突，要重新建立後再 cancel 舊的。
# ReservationDTO.previous_reserve 可紀錄前一次的[reserve_id]，以便找到同樣的討論串/變更原因歷史。
# 如果 "previous_reserve" 不為空，則表示這是一次變更預約的操作 => 新增後，將舊的預約設為 cancel。
############################################################################################
@router.post('/{user_id}/reservations',
             responses=post_response('new_booking', reservation.ReservationVO))
async def new_booking(
        user_id: int = Path(...),
        body: reservation.ReservationDTO = Body(...),
):
    body.my_user_id = user_id
    body.my_status = BookingStatus.ACCEPT
    res: Dict = await _user_service.new_booking(body)
    return res_success(data=res)


@router.put('/{user_id}/reservations/{reservation_id}',
            responses=idempotent_response('update_reservation_status', reservation.ReservationVO))
async def update_reservation_status(
        user_id: int = Path(...),
        reservation_id: int = Path(...),
        body: reservation.UpdateReservationDTO = Body(...),
):
    body.my_user_id = user_id
    res: Dict = await _user_service.update_reservation_status(reservation_id, body)
    return res_success(data=res)
