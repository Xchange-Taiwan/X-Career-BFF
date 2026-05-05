import logging
from typing import List, Optional

from pydantic import BaseModel, Field

from .experience_model import ExperienceVO
from ...user.model.user_model import ProfileDTO, ProfileVO
from ....config.constant import (
    ScheduleType,
    SeniorityLevel,
    TimeSlotType,
)

log = logging.getLogger(__name__)


class MentorProfileDTO(ProfileDTO):
    """與 X-Career-User `MentorProfileDTO` 欄位一致。"""

    personal_statement: Optional[str] = None
    about: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = SeniorityLevel.NO_REVEAL

    class Config:
        from_attributes = True


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str] = ""
    about: Optional[str] = ""
    seniority_level: Optional[SeniorityLevel] = SeniorityLevel.NO_REVEAL
    experiences: Optional[List[ExperienceVO]] = Field(default_factory=list)


class TimeSlotDTO(BaseModel):
    id: Optional[int] = Field(None, example=0)
    user_id: int = Field(..., example=1)
    dt_type: TimeSlotType = Field(..., example=TimeSlotType.ALLOW)
    dt_year: Optional[int] = Field(default=None, example=2024)
    dt_month: Optional[int] = Field(default=None, example=6)
    dtstart: int = Field(..., example=1717203600)
    dtend: int = Field(..., example=1717207200)
    rrule: Optional[str] = Field(default=None, example="FREQ=WEEKLY;COUNT=4")
    timezone: str = Field(default="UTC", example="UTC")
    exdate: List[Optional[int]] = Field(default=[], example=[1718413200, 1719622800])
    # New-format marker mirrored from X-Career-User. NULL = legacy
    # MINUTELY-rrule row; set = (dtstart, dtend) is block, divided into
    # sub-slots of this length. Must flow through unchanged.
    meeting_duration_minutes: Optional[int] = Field(default=None, example=30)


class MentorScheduleDTO(BaseModel):
    until: int = Field(default=None, example=1735689600)
    timeslots: List[TimeSlotDTO] = Field(default=[])


class TimeSlotVO(TimeSlotDTO):
    id: int = Field(..., example=0)


class MentorScheduleVO(BaseModel):
    timeslots: Optional[List[TimeSlotVO]] = Field(default=[])
    next_dtstart: Optional[int] = Field(default=None, example=0)


class MentorScheduleSegmentVO(BaseModel):
    id: Optional[int] = Field(default=None, example=0)
    user_id: int = Field(..., example=1)
    dt_type: ScheduleType = Field(..., example=ScheduleType.ALLOW)
    dtstart: int = Field(..., example=1717203600)
    dtend: int = Field(..., example=1717207200)
    rrule: Optional[str] = Field(default=None, example="FREQ=WEEKLY;COUNT=4")
    timezone: str = Field(default="UTC", example="UTC")
    exdate: List[Optional[int]] = Field(default=[], example=[1718413200, 1719622800])
    meeting_duration_minutes: Optional[int] = Field(default=None, example=30)
    source: str = Field(..., example="schedule")
    source_id: Optional[int] = Field(default=None, example=100)


class MentorScheduleQueryVO(BaseModel):
    segments: Optional[List[MentorScheduleSegmentVO]] = Field(default=[])
    next_dtstart: Optional[int] = Field(default=None, example=0)
