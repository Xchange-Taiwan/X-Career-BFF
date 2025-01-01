from pydantic import BaseModel, Field
from ...user.model.common_model import (
    ProfessionDTO,
    ProfessionListVO,
)
from ...user.model.user_model import *
from .experience_model import ExperienceVO
from ....config.conf import *
from ....config.constant import *


log.basicConfig(filemode="w", level=log.INFO)


class MentorProfileDTO(ProfileDTO):
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[str] = "NO REVEAL"
    expertises: Optional[List[ProfessionDTO]] = []


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str] = ""
    about: Optional[str] = ""
    seniority_level: Optional[str] = ""
    expertises: Optional[ProfessionListVO] = None
    experiences: Optional[List[ExperienceVO]] = []


class TimeSlotDTO(BaseModel):
    id: Optional[int] = Field(None, example=0)
    user_id: int = Field(..., example=1)
    dt_type: str = Field(
        ..., example=AVAILABLE_EVT, pattern=f"^({AVAILABLE_EVT}|{UNAVAILABLE_EVT})$"
    )
    dt_year: Optional[int] = Field(default=None, example=2024)
    dt_month: Optional[int] = Field(default=None, example=6)
    dtstart: int = Field(..., example=1717203600)
    dtend: int = Field(..., example=1717207200)
    timezone: str = Field(default="UTC", example="UTC")
    rrule: Optional[str] = Field(default=None, example="FREQ=WEEKLY;COUNT=4")
    exdate: List[Optional[int]] = Field(default=[], example=[1718413200, 1719622800])


class MentorScheduleDTO(BaseModel):
    until: int = Field(default=None, example=1735689600)
    timeslots: List[TimeSlotDTO] = Field(default=[])


class TimeSlotVO(TimeSlotDTO):
    id: int = Field(..., example=0)


class MentorScheduleVO(BaseModel):
    timeslots: Optional[List[TimeSlotVO]] = Field(default=[])
    next_dtstart: Optional[int] = Field(default=None, example=0)
