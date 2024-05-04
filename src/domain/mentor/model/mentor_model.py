from sqlalchemy import Column, Integer, String, ForeignKey
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


class Mentor(Base):
    __tablename__ = 'mentor_profile'

    mentor_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    personal_statement = Column(String)
    seniority_level = Column(String)
    about = Column(String)


class MentorExpertisesInter(Base):
    __tablename__ = 'mentor_expertises_inter'

    expertises_id = Column(Integer, ForeignKey("mentor_expertises.expertises_id"), autoincrement=True, primary_key=True,
                           nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentor_profile.mentor_id"), autoincrement=True, primary_key=True,
                       nullable=False)


class MentorExpertises(Base):
    __tablename__ = 'mentor_expertises'

    expertises_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    expertises = Column(String)
    industry = Column(String)
    subject = Column(String)
    inter = relationship("MentorExpertisesInter", cascade="all, delete-orphan")


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
