from enum import Enum


class SeniorityLevel(Enum):
    NO_REVEAL = 'No reveal'
    JUNIOR = 'junior'
    INTERMEDIATE = 'intermediate'
    SENIOR = 'senior'
    STAFF = 'staff'
    MANAGER = 'manager'


class ScheduleType(Enum):
    ALLOW = 'allow'
    FORBIDDEN = 'forbidden'
