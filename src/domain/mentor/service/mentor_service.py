from sqlalchemy.orm import Session

from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.mentor.dao.mentor_repository import MentorRepository
from src.domain.mentor.model.mentor_model import MentorProfileDTO, MentorProfileVO


class MentorService:
    def __init__(self, mentor_repository: MentorRepository, interest_repository: InterestRepository):
        self.__mentor_repository: MentorRepository = mentor_repository
        self.__interest_repository: InterestRepository = interest_repository

    def upsert_mentor_profile(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        res_dto: MentorProfileDTO = self.__mentor_repository.upsert_mentor(mentor_profile_dto, db)
        res_vo: MentorProfileVO = self.convert_to_mentor_profile_VO(res_dto, db)
        db.commit()
        return res_vo

    def get_mentor_profile_by_id(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        return self.convert_to_mentor_profile_VO(
            self.__mentor_repository.get_mentor_profile_by_id(mentor_profile_dto, db))

    def convert_to_mentor_profile_VO(self, dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        dic = dto.dict(exclude={"industry", "expertises", "skills", "topics"})
        res = MentorProfileVO(**dic)

        if (dto.skills is not None):
            res.skills = self.__interest_repository.get_interest_by_ids(dto.skills, db)
        if (dto.topics is not None):
            res.topics = self.__interest_repository.get_interest_by_ids(dto.topics, db)

        # res.user_id = dto.mentor_profile_id
        # res.industry = dto.industry
        return res
