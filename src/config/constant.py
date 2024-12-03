import string
from enum import Enum
import os


class InterestCategory(Enum):
    INTERESTED_POSITION = 'interested_position'
    SKILL = 'skill'
    TOPIC = 'topic'


class ProfessionCategory(Enum):
    EXPERTISE = 'expertise'
    INDUSTRY = 'industry'


class ExperienceCategory(Enum):
    WORK = 'work'
    EDUCATION = 'education'
    LINK = 'link'


class ScheduleType(Enum):
    ALLOW = 'allow'
    FORBIDDEN = 'forbidden'


class RoleType(Enum):
    MENTOR = 'mentor'
    MENTEE = 'mentee'


class BookingStatus(Enum):
    PENDING = 'pending'
    ACCEPT = 'accept'
    REJECT = 'reject'


class ReservationListState(Enum):
    UPCOMING = 'upcoming'
    PENDING = 'pending'
    HISTORY = 'history'


class SortingBy(Enum):
    UPDATED_TIME = 'updated_time'
    # VIEW = 'view'


class Sorting(Enum):
    ASC = 1
    DESC = -1


# serial_key is a field of the collection in the user's cache
SERIAL_KEY = 'created_at'

# the amount of prefetch items from match data
PREFETCH = 3

# Accessing environment variables with default values
# TODO: 參考 AUTH_SERVICE_URL 的用法，不需要這麼冗長; 另外 "/v1" 直接寫在每個 api path 裡如何?
USER_SERVICE_PREFIX: str = "/user-service"
MENTORS = 'mentors'
FILE = 'file'
USERS = 'users'
PROFILE = 'profile'
