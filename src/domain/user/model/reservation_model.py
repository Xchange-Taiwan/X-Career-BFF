import logging as log

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from .user_model import *
from ....config.constant import *
from ....config.conf import BATCH


log.basicConfig(filemode='w', level=log.INFO)


class ReservationQueryDTO(BaseModel):
    state: str = Field(
        None,
        example=ReservationListState.UPCOMING.value,
        pattern=f'^({ReservationListState.UPCOMING.value}|{ReservationListState.PENDING.value}|{ReservationListState.HISTORY.value})$',
    )
    batch: int = Field(..., example=BATCH, ge=1)
    next_dtend: Optional[int] = Field(None, example=1735398000)


class UpdateReservationDTO(BaseModel):
    my_user_id: int = 0
    my_status: Optional[BookingStatus] = Field(None, example=BookingStatus.PENDING)
    user_id: int = 0
    schedule_id: int = 0
    dtstart: int = 0  # timestamp
    dtend: int = 0  # timestamp
    messages: Optional[List[Dict[str, Any]]] = []

    def participant_query(self) -> Dict:
        return {
            'my_user_id': self.user_id,
            'schedule_id': self.schedule_id,
            'dtstart': self.dtstart,
            'dtend': self.dtend,
            'user_id': self.my_user_id,
        }


'''
讓後端實現「先建立再取消」:
    1. 新建一筆預約，寫上新的 reservation_id (reserve_id);
        並在欄位'previous_reserve' 存儲前一次的[reserve_id]，以便找到同樣的討論串
    2. 將舊的預約設為 cancel
'''


class ReservationDTO(UpdateReservationDTO):
    # sender's previous reservation
    previous_reserve: Optional[Dict[str, Any]] = None


class RUserInfoVO(BaseModel):
    user_id: Optional[int] = Field(None, example=0)
    # role: Optional[str] = Field(None, example=RoleType.MENTEE.value,
    #                      pattern=f'^({RoleType.MENTOR.value}|{RoleType.MENTEE.value})$')
    status: Optional[str] = Field(
        None,
        example=BookingStatus.PENDING.value,
        pattern=f'^({BookingStatus.ACCEPT.value}|{BookingStatus.REJECT.value}|{BookingStatus.PENDING.value})$',
    )
    name: Optional[str] = ''
    avatar: Optional[str] = ''
    job_title: Optional[str] = ''
    years_of_experience: Optional[int] = 0


class ReservationVO(ReservationDTO):
    id: Optional[int] = None  # id: int 因為沒有經過 await db.refresh()，所以不會有 id
    status: Optional[BookingStatus] = Field(None, example=BookingStatus.PENDING)


class ReservationMessageVO(BaseModel):
    user_id: int = Field(None, example=0)
    # role: Optional[str] = Field(..., example=RoleType.MENTEE.value,
    #                      pattern=f'^({RoleType.MENTOR.value}|{RoleType.MENTEE.value})$')
    content: str = Field(None, example='')


class ReservationInfoVO(BaseModel):
    id: Optional[int] = None
    sender: RUserInfoVO  # sharding key: sneder.user_id
    participant: RUserInfoVO
    schedule_id: int = 0
    dtstart: int = 0  # timestamp
    dtend: int = 0  # timestamp
    previous_reserve: Optional[Dict[str, Any]] = None
    messages: Optional[List[ReservationMessageVO]] = []


class ReservationInfoListVO(BaseModel):
    reservations: Optional[List[ReservationInfoVO]] = []
    next_dtend: Optional[int] = 0
