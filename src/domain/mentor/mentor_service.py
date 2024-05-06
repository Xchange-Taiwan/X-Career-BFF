from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.mentor_repostory import MentorRepository
from src.domain.mentor.model.mentor_model import MentorProfileDTO, MentorProfileVO, MentorExpertisesVo


class MentorService:
    def __init__(self, mentor_repository: MentorRepository):
        self.__mentor_repository: MentorRepository = mentor_repository

    def upsert_mentor_profile(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        res: MentorProfileDTO = self.__mentor_repository.upsert_mentor(mentor_profile_dto, db)


        return res

    def get_mentor_profile_by_id(self, mentor_profile_dto):
        return self.__mentor_repository.get_mentor_profile_by_id(mentor_profile_dto)
