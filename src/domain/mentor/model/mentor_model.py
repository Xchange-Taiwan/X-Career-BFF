from ...user.model.common_model import (
    ProfessionDTO, ProfessionListVO,
)
from ...user.model.user_model import *
from .experience_model import ExperienceVO
from ....config.conf import *
from ....config.constant import *

log.basicConfig(filemode='w', level=log.INFO)


class MentorProfileDTO(ProfileDTO):
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[str] = 'NO REVEAL'
    expertises: Optional[List[str]] = []


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str] = ""
    about: Optional[str] = ""
    seniority_level: Optional[str] = ""
    expertises: Optional[ProfessionListVO] = None
    experiences: Optional[List[ExperienceVO]] = []


class TimeSlotDTO(BaseModel):
    schedule_id: Optional[int]
    type: ScheduleType
    year: int = SCHEDULE_YEAR
    month: int = SCHEDULE_MONTH
    day_of_month: int = SCHEDULE_DAY_OF_MONTH
    day_of_week: int = SCHEDULE_DAY_OF_WEEK
    start_time: int
    end_time: int


class TimeSlotVO(TimeSlotDTO):
    schedule_id: int


class MentorScheduleVO(BaseModel):
    timeslots: Optional[List[TimeSlotVO]] = []
    next_id: Optional[int]
