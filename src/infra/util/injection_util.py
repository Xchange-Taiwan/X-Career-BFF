# Dependency function to create DAO instance
from fastapi import Depends

from src.domain.mentor.mentor_repostory import MentorRepository
from src.domain.mentor.mentor_service import MentorService


def get_mentor_dao() -> MentorRepository:
    return MentorRepository()


# Dependency function to create UserService instance with UserDAO dependency injected
def get_mentor_service(mentor_dao: MentorRepository = Depends(get_mentor_dao)) -> MentorService:
    return MentorService(mentor_dao)
