# Dependency function to create DAO instance
from fastapi import Depends

from src.domain.mentor.dao.industry_repository import ProfessionRepository
from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.mentor.dao.mentor_repository import MentorRepository
from src.domain.mentor.service.mentor_service import MentorService
from src.domain.user.dao.profile_repository import ProfileRepository
from src.domain.user.service.interest_service import InterestService
from src.domain.user.service.profession_service import ProfessionService
from src.domain.user.service.profile_service import ProfileService


def get_mentor_dao() -> MentorRepository:
    return MentorRepository()


def get_interest_dao() -> InterestRepository:
    return InterestRepository()


def get_profile_dao() -> ProfileRepository:
    return ProfileRepository()


def get_profession_dao() -> ProfessionRepository:
    return ProfessionRepository()


def get_interest_service(interest_repo: InterestRepository = Depends(get_interest_dao)):
    return InterestService(interest_repo)


def get_profession_service(
        profession_repository: ProfessionRepository = Depends(get_profession_dao)) -> ProfessionService:
    return ProfessionService(profession_repository)


# Dependency function to create Service instance with DAO dependency injected
def get_mentor_service(mentor_repository: MentorRepository = Depends(get_mentor_dao),
                       interest_repository: InterestRepository = Depends(get_interest_dao),
                       profile_repository: ProfileRepository = Depends(get_profile_dao),
                       profession_repository: ProfessionRepository = Depends(get_profession_dao)
                       ) -> MentorService:
    return MentorService(mentor_repository, interest_repository, profile_repository, profession_repository)


def get_profile_service(
        interest_service: InterestService = Depends(get_interest_service),
        profile_repository: ProfileRepository = Depends(get_profile_dao),
        profession_service: ProfessionService = Depends(get_profession_service)) -> ProfileService:
    return ProfileService(interest_service, profile_repository, profession_service)


def get_interest_service(interest_dao: InterestRepository = Depends(get_interest_dao)):
    return InterestService(interest_dao)


def get_profession_service(profession_repository: ProfessionRepository = Depends(get_profession_dao)):
    return ProfessionService(profession_repository)
