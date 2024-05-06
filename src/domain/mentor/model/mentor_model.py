from sqlalchemy import Column, Integer, String, ForeignKey, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ...user.model.common_model import (
    ProfessionDTO,
)
from ...user.model.user_model import *
from ....config.conf import *
from ....config.constant import *

log.basicConfig(filemode='w', level=log.INFO)
Base = declarative_base()


class SeniorityLevel(Enum):
    NO_REVEAL = 'No reveal'
    JUNIOR = 'junior'
    INTERMEDIATE = 'intermediate'
    SENIOR = 'senior'
    STAFF = 'staff'
    MANAGER = 'manager'


class Category(Enum):
    NO_REVEAL = 'No reveal'
    OUTDOOR = 'outdoor'
    INDOOR = 'indoor'


class SchedulesStatus(Enum):
    ALLOW = 'allow'
    FORBIDDEN = 'forbidden'


class AcceptStatus(Enum):
    ACCEPT = 'accept'
    PENDING = 'pending'
    REJECT = 'reject'


class MemberRole(Enum):
    MENTOR = 'mentor'
    MENTEE = 'mentee'


class MentorProfile(Base):
    __tablename__ = 'mentor_profile'

    mentor_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    avatar = Column(String, default='')
    location = Column(String, default='')
    industry = Column(String, default='')
    position = Column(String, default='')
    linkedin_profile = Column(String, default='')
    personal_statement = Column(Text, default='')
    about = Column(Text, default='')
    seniority_level = Column(Enum(SeniorityLevel), nullable=False)
    timezone = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    interested_positions = Column(JSONB)
    skills = Column(JSONB)
    topics = Column(JSONB)
    expertises = Column(JSONB)


class MentorExperiences(Base):
    __tablename__ = 'mentor_experiences'

    experiences_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    category = Column(Enum(Category), nullable=False)
    order = Column(Integer, nullable=False)
    metadata = Column(JSONB)


class Professions(Base):
    __tablename__ = 'professions'

    professions_id = Column(Integer, primary_key=True)
    category = Column(Enum(Category), default=Category.NO_REVEAL)
    subject = Column(String, default='')
    metadata = Column(JSONB)


class MentorSchedules(Base):
    __tablename__ = 'mentor_schedules'

    mentor_schedules_id = Column(Integer, primary_key=True)
    type = Column(Enum(SchedulesStatus), default=SchedulesStatus.ALLOW)
    year = Column(Integer, default=-1)
    month = Column(Integer, default=-1)
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    cycle_start_date = Column(BigInteger)
    cycle_end_date = Column(BigInteger)


class CannedMessage(Base):
    __tablename__ = 'canned_message'

    canned_message_id = Column(Integer, primary_key=True)
    user_id = Column(Enum(Category), nullable=False)
    role = Column(Enum(MemberRole), nullable=False)
    message = Column(Text)


class Reservations(Base):
    __tablename__ = 'reservations'

    reservations_id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, nullable=False)
    mentee_id = Column(Integer, nullable=False)
    start_datetime = Column(BigInteger)
    end_datetime = Column(BigInteger)
    my_status = Column(Enum(AcceptStatus), nullable=False, default=AcceptStatus.PENDING)
    status = Column(Enum(AcceptStatus), nullable=False, default=AcceptStatus.PENDING)
    role = Column(Enum(MemberRole))
    message_from_others = Column(Text, default='')


class MentorProfileDTO(BaseModel):
    id: Optional[int]
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[str] = ""
    expertises: Optional[List[ProfessionDTO]] = []


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[str] = ""
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


class MentorExpertisesDto(BaseModel):
    expertises_id: int
    mentor_id: int


class MentorExpertisesVo(BaseModel):
    expertises_id: int
    expertises: str
    industry = str
    subject: str
