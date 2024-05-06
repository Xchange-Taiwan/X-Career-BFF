from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Intege, Text, BigInteger, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base

from src.config.constant import RoleType, BookingStatus
from src.domain.mentor.enum.mentor_enums import SchedulesType

Base = declarative_base()

class MentorSchedules(Base):
    __tablename__ = 'mentor_schedules'

    mentor_schedules_id = Column(Integer, primary_key=True)
    type = Column(Enum(SchedulesType), default=SchedulesType.ALLOW)
    year = Column(Integer, default=-1)
    month = Column(Integer, default=-1)
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    cycle_start_date = Column(BigInteger)
    cycle_end_date = Column(BigInteger)


class Reservations(Base):
    __tablename__ = 'reservations'

    reservations_id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, nullable=False)
    mentee_id = Column(Integer, nullable=False)
    start_datetime = Column(BigInteger)
    end_datetime = Column(BigInteger)
    my_status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    role = Column(Enum(RoleType))
    message_from_others = Column(Text, default='')


class MentorSchedulesDTO(BaseModel):
    mentor_schedules_id: int
    type: str
    year: int = -1
    month: int = -1
    day_of_month: int
    day_of_week: int
    start_time: int
    end_time: int
    cycle_start_date: Optional[int] = None
    cycle_end_date: Optional[int] = None


class ReservationsDTO(BaseModel):
    reservations_id: int
    mentor_id: int
    mentee_id: int
    start_datetime: Optional[int] = None
    end_datetime: Optional[int] = None
    my_status: str = 'pending'
    status: str = 'pending'
    role: Optional[str] = None
    message_from_others: Optional[str] = ''
