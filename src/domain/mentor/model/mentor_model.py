from pydantic import Field

from .experience_model import ExperienceVO
from ...user.model.common_model import ProfessionListVO
from ...user.model.user_model import *
from ....config.constant import *

log = logging.getLogger(__name__)


class MentorProfileDTO(ProfileDTO):
    """與 X-Career-User `MentorProfileDTO` 欄位一致。"""

    personal_statement: Optional[str] = None
    about: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = SeniorityLevel.NO_REVEAL
    expertises: Optional[List[str]] = None

    class Config:
        from_attributes = True


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str] = ""
    about: Optional[str] = ""
    seniority_level: Optional[SeniorityLevel] = SeniorityLevel.NO_REVEAL
    expertises: Optional[ProfessionListVO] = None
    experiences: Optional[List[ExperienceVO]] = Field(default_factory=list)


class TimeSlotDTO(BaseModel):
    id: Optional[int] = Field(None, example=0)
    user_id: int = Field(..., example=1)
    dt_type: str = Field(
        ...,
        example=ScheduleType.ALLOW.value,
        pattern=f"^({ScheduleType.ALLOW.value}|{ScheduleType.FORBIDDEN.value})$",
    )
    dt_year: Optional[int] = Field(default=None, example=2024)
    dt_month: Optional[int] = Field(default=None, example=6)
    dtstart: int = Field(..., example=1717203600)
    dtend: int = Field(..., example=1717207200)
    rrule: Optional[str] = Field(default=None, example="FREQ=WEEKLY;COUNT=4")
    # timezone: str = Field(default="UTC", example="UTC")
    # exdate: List[Optional[int]] = Field(default=[], example=[1718413200, 1719622800])


class MentorScheduleDTO(BaseModel):
    until: int = Field(default=None, example=1735689600)
    timeslots: List[TimeSlotDTO] = Field(default=[])


class TimeSlotVO(TimeSlotDTO):
    id: int = Field(..., example=0)


class MentorScheduleVO(BaseModel):
    timeslots: Optional[List[TimeSlotVO]] = Field(default=[])
    next_dtstart: Optional[int] = Field(default=None, example=0)
