from pydantic import Field

from .experience_model import ExperienceVO
from ...user.model.common_model import ProfessionListVO
from ...user.model.tag_model import TagVO
from ...user.model.user_model import *
from ....config.constant import *

log = logging.getLogger(__name__)


class MentorProfileDTO(ProfileDTO):
    """與 X-Career-User `MentorProfileDTO` 欄位一致。"""

    personal_statement: Optional[str] = None
    about: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = SeniorityLevel.NO_REVEAL
    expertises: Optional[List[str]] = None

    # Per-bucket replace: None = leave alone, [] = clear, [...] = replace.
    # Each entry is a leaf subject_group; User-service validates against the
    # tags catalog and aggregates into want_tags / have_tags before storage.
    want_position: Optional[List[str]] = None
    want_skill: Optional[List[str]] = None
    want_topic: Optional[List[str]] = None
    have_skill: Optional[List[str]] = None
    have_topic: Optional[List[str]] = None

    class Config:
        from_attributes = True


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str] = ""
    about: Optional[str] = ""
    seniority_level: Optional[SeniorityLevel] = SeniorityLevel.NO_REVEAL
    expertises: Optional[ProfessionListVO] = None
    experiences: Optional[List[ExperienceVO]] = Field(default_factory=list)

    # Hydrated by User-service: each TagVO carries subject + desc +
    # parent_subject_group from the catalog.
    want_position: Optional[List[TagVO]] = None
    want_skill: Optional[List[TagVO]] = None
    want_topic: Optional[List[TagVO]] = None
    have_skill: Optional[List[TagVO]] = None
    have_topic: Optional[List[TagVO]] = None


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
    source: str = Field(..., example="schedule")
    source_id: Optional[int] = Field(default=None, example=100)


class MentorScheduleQueryVO(BaseModel):
    segments: Optional[List[MentorScheduleSegmentVO]] = Field(default=[])
    next_dtstart: Optional[int] = Field(default=None, example=0)
