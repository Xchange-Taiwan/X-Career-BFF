from enum import Enum


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


class IndustryCategory(Enum):
    SOFTWARE = 'software'
    HARDWARE = 'hardware'
    SERVICE = 'service'
    FINANCE = 'finance'
    OTHER = 'other'


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


class SchedulesType(Enum):
    ALLOW = "allow"
    FORBIDDEN = "forbidden"


# serial_key is a field of the collection in the user's cache
SERIAL_KEY = 'created_at'

# the amount of prefetch items from match data
PREFETCH = 3
