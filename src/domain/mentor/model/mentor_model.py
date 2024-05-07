from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types
from ..enum.mentor_enums import SeniorityLevel, ScheduleType
from ...user.model.user_model import *
from ....config.conf import *
from ....config.constant import *

log.basicConfig(filemode='w', level=log.INFO)
Base = declarative_base()


class MentorProfile(Base):
    __tablename__ = 'mentor_profile'

    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    avatar = Column(String, default='')
    location = Column(String, default='')
    position = Column(String, default='')
    linkedin_profile = Column(String, default='')
    personal_statement = Column(Text, default='')
    about = Column(Text, default='')
    seniority_level = Column(types.Enum(SeniorityLevel), nullable=False)
    timezone = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    company = Column(Text, default='')
    interested_positions = Column(JSONB)
    skills = Column(JSONB)
    topics = Column(JSONB)
    industry = Column(JSONB)
    expertises = Column(JSONB)


class MentorExperiences(Base):
    __tablename__ = 'mentor_experiences'

    mentor_experiences_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    category = Column(types.Enum(ProfessionCategory), nullable=False)
    order = Column(Integer, nullable=False)
    experiences_metadata = Column(JSONB)


class Professions(Base):
    __tablename__ = 'professions'

    professions_id = Column(Integer, primary_key=True)
    category = Column(types.Enum(ProfessionCategory))
    subject = Column(String, default='')
    professions_metadata = Column(JSONB)


class CannedMessage(Base):
    __tablename__ = 'canned_message'

    canned_message_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    role = Column(types.Enum(RoleType), nullable=False)
    message = Column(Text)


class Interests(Base):
    __tablename__ = 'interests'
    id = Column(Integer, primary_key=True)
    category = Column(types.Enum(InterestCategory), nullable=False)
    subject = Column(String, nullable=False)
    desc = Column(JSONB)


# class MentorProfileDTO(BaseModel):
#     mentor_profile_id: Optional[int]
#     avatar: Optional[str]
#     location: Optional[str]
#     timezone: Optional[int]
#     experience: Optional[int]
#
#     personal_statement: Optional[str]
#     about: Optional[str]
#     # TODO: enum
#     seniority_level: Optional[str] = ""
#     expertises: Optional[List[ProfessionDTO]] = []


class MentorProfileDTO(ProfileDTO):
    user_id: Optional[int]
    location: Optional[str] = ''
    personal_statement: Optional[str] = ''
    about: Optional[str] = ''
    seniority_level: Optional[SeniorityLevel]
    experience: Optional[int] = 0
    expertises: Optional[List[int]] = []


class MentorExperiencesDTO(BaseModel):
    mentor_experiences_id: int
    user_id: int
    category: Optional[str]
    order: Optional[int]
    mentor_experiences_metadata: Optional[Dict] = {}


class ProfessionsDTO(BaseModel):
    professions_id: int
    category: Optional[str]
    subject: Optional[str] = ''
    professions_metadata: Optional[Dict] = {}


class CannedMessageDTO(BaseModel):
    canned_message_id: int
    user_id: int
    role: Optional[str]
    message: Optional[str]


class MentorProfileVO(ProfileVO):
    personal_statement: Optional[str]
    about: Optional[str]
    # TODO: enum
    seniority_level: Optional[SeniorityLevel] = ""
    expertises: Optional[List[ProfessionVO]]


class TimeSlotDTO(BaseModel):
    schedule_id: Optional[int]
    type: ScheduleType
    year: Optional[int] = SCHEDULE_YEAR
    month: Optional[int] = SCHEDULE_MONTH
    day_of_month: Optional[int] = SCHEDULE_DAY_OF_MONTH
    day_of_week: Optional[int] = SCHEDULE_DAY_OF_WEEK
    start_time: Optional[int]
    end_time: Optional[int]


class TimeSlotVO(TimeSlotDTO):
    schedule_id: int


class MentorScheduleVO(BaseModel):
    timeslots: Optional[List[TimeSlotVO]] = []
    next_id: Optional[int]


class MentorExpertisesVo(BaseModel):
    expertises_id: int
    expertises: str
    industry = str
    subject: str
