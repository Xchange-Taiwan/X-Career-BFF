import string
from enum import Enum
import os


class Language(Enum):
    EN_US = 'en_US'
    ZH_TW = 'zh_TW'


class InterestCategory(Enum):
    INTERESTED_POSITION = 'INTERESTED_POSITION'
    SKILL = 'SKILL'
    TOPIC = 'TOPIC'


class ProfessionCategory(Enum):
    EXPERTISE = 'EXPERTISE'
    INDUSTRY = 'INDUSTRY'


class ExperienceCategory(Enum):
    WORK = 'WORK'
    EDUCATION = 'EDUCATION'
    LINK = 'LINK'


class ScheduleType(Enum):
    ALLOW = 'ALLOW'
    FORBIDDEN = 'FORBIDDEN'


class RoleType(Enum):
    MENTOR = 'MENTOR'
    MENTEE = 'MENTEE'


class BookingStatus(Enum):
    PENDING = 'PENDING'
    ACCEPT = 'ACCEPT'
    REJECT = 'REJECT'


class ReservationListState(Enum):
    UPCOMING = 'UPCOMING'
    PENDING = 'PENDING'
    HISTORY = 'HISTORY'


class SortingBy(Enum):
    UPDATED_TIME = 'UPDATED_TIME'
    # VIEW = 'VIEW'


class Sorting(Enum):
    ASC = 1
    DESC = -1


class SchedulesType(Enum):
    ALLOW = "ALLOW"
    FORBIDDEN = "FORBIDDEN"


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


# schedule event types: AVAILABLE, UNAVAILABLE
AVAILABLE_EVT = 'AVAILABLE'
UNAVAILABLE_EVT = 'UNAVAILABLE'
