# Dependency function to create DAO instance
from fastapi import Depends

from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.mentor.dao.mentor_repository import MentorRepository
from src.domain.mentor.service.mentor_service import MentorService


def get_mentor_dao() -> MentorRepository:
    return MentorRepository()


def get_interest_dao() -> InterestRepository:
    return InterestRepository()


# Dependency function to create UserService instance with UserDAO dependency injected
def get_mentor_service(mentor_dao: MentorRepository = Depends(get_mentor_dao),
                       interest_dao: InterestRepository = Depends(get_interest_dao)) -> MentorService:
    return MentorService(mentor_dao, interest_dao)
