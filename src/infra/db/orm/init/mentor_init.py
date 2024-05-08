from sqlalchemy import Integer, Column, String, types, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.config.constant import ProfessionCategory, RoleType, InterestCategory, SchedulesType, BookingStatus, \
    IndustryCategory
from src.domain.mentor.enum.mentor_enums import SeniorityLevel
Base = declarative_base()


class Profile(Base):
    __tablename__ = 'profiles'
    user_id = Column(String, ForeignKey('accounts.user.id'), primary_key=True)
    name = Column(String, nullable=False)
    avatar = Column(String, default='')
    location = Column(String, default='')
    position = Column(String, default='')
    linkedin_profile = Column(String, default='')
    personal_statement = Column(String, default='')
    about = Column(String, default='')
    company = Column(String, default='')
    seniority_level = Column(types.Enum(SeniorityLevel), nullable=False)
    timezone = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    industry = Column(Integer)
    interested_positions = Column(JSONB)
    skills = Column(JSONB)
    topics = Column(JSONB)
    expertises = Column(JSONB)



class MentorExperience(Base):
    __tablename__ = 'mentor_experiences'
    mentor_experiences_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('profiles.user_id'), nullable=False)
    category = Column(types.Enum(ProfessionCategory), nullable=False)
    order = Column(Integer, nullable=False)
    mentor_experiences_metadata = Column(JSONB)
    #profile = relationship("Profile", backref="mentor_experiences")


class Profession(Base):
    __tablename__ = 'professions'
    professions_id = Column(Integer, primary_key=True)
    profession_category = Column(types.Enum(ProfessionCategory))
    subject = Column(String, default='')
    professions_metadata = Column(JSONB)


class MentorSchedule(Base):
    __tablename__ = 'mentor_schedules'
    mentor_schedules_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('profiles.user_id'), nullable=False)
    type = Column(types.Enum(SchedulesType), default='ALLOW')
    year = Column(Integer, default=-1)
    month = Column(Integer, default=-1)
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    cycle_start_date = Column(Integer)
    cycle_end_date = Column(Integer)
    #profile = relationship("Profile", backref="mentor_schedules")


class CannedMessage(Base):
    __tablename__ = 'canned_message'
    canned_message_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('profiles.user_id'), nullable=False)
    role = Column(types.Enum(RoleType), nullable=False)
    message = Column(String)
    #profile = relationship("Profile", backref="canned_message")


class Reservation(Base):
    __tablename__ = 'reservations'
    reservations_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('profiles.user_id'), nullable=False)
    mentor_schedules_id = Column(Integer, ForeignKey('mentor_schedules.mentor_schedules_id'), nullable=False)
    start_datetime = Column(Integer)
    end_datetime = Column(Integer)
    my_status = Column(types.Enum(BookingStatus))
    status = Column(types.Enum(BookingStatus))
    role = Column(types.Enum(RoleType))
    message_from_others = Column(String, default='')
    #profile = relationship("Profile", backref="reservations")
    #mentor_schedule = relationship("MentorSchedule", backref="reservations")


class Interest(Base):
    __tablename__ = 'interests'
    id = Column(Integer, primary_key=True)
    category = Column(types.Enum(InterestCategory))
    subject = Column(String)
    desc = Column(JSONB)


class Industry(Base):
    __tablename__ = 'industries'
    id = Column(Integer, primary_key=True)
    profession_category = Column(types.Enum(ProfessionCategory))
    subject = Column(String)
    industry_metadata = Column(JSONB)
