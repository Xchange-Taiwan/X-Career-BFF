from ...user.model.common_model import (
    ProfessionDTO,
)
from ...user.model.user_model import *
from ....config.conf import *
from ....config.constant import *

log.basicConfig(filemode='w', level=log.INFO)


class MentorProfileDTO(ProfileDTO):
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[str] = []
    expertises: Optional[List[ProfessionDTO]] = []


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[str] = []
    expertises: Optional[List[ProfessionVO]] = []


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
