# Dependency function to create DAO instance
from fastapi import Depends

from src.domain.mentor.dao.industry_repository import IndustryRepository
from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.mentor.dao.mentor_repository import MentorRepository
from src.domain.mentor.dao.profile_repository import ProfileRepository
from src.domain.mentor.service.mentor_service import MentorService
from src.domain.user.service.industry_service import IndustryService
from src.domain.user.service.interest_service import InterestService


def get_mentor_dao() -> MentorRepository:
    return MentorRepository()


def get_interest_dao() -> InterestRepository:
    return InterestRepository()


def get_profile_dao() -> ProfileRepository:
    return ProfileRepository()


def get_industry_dao() -> IndustryRepository:
    return IndustryRepository()


# Dependency function to create Service instance with DAO dependency injected
def get_mentor_service(mentor_dao: MentorRepository = Depends(get_mentor_dao),
                       interest_dao: InterestRepository = Depends(get_interest_dao),
                       profile_dao: ProfileRepository = Depends(get_profile_dao),
                       industry_dao: IndustryRepository = Depends(get_industry_dao)
                       ) -> MentorService:
    return MentorService(mentor_dao, interest_dao, profile_dao, industry_dao)

def get_interest_service(interest_dao: InterestRepository = Depends(get_interest_dao)):
    return InterestService(interest_dao)

def get_industry_service(industry_dao: IndustryRepository = Depends(get_industry_dao)):
    return IndustryService(industry_dao)