from sqlalchemy.orm import Session

from src.domain.mentor.dao.industry_repository import IndustryRepository
from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.mentor.dao.mentor_repository import MentorRepository
from src.domain.mentor.dao.profile_repository import ProfileRepository
from src.domain.mentor.model.mentor_model import MentorProfileDTO, MentorProfileVO


class MentorService:
    def __init__(self, mentor_repository: MentorRepository,
                 interest_repository: InterestRepository,
                 profile_repository: ProfileRepository,
                 industry_repository: IndustryRepository):
        self.__mentor_repository: MentorRepository = mentor_repository
        self.__interest_repository: InterestRepository = interest_repository
        self.__industry_repository: IndustryRepository = industry_repository
        self.__profile_repository = profile_repository

    def upsert_profile(self, profile_dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        res_dto: MentorProfileDTO = self.__mentor_repository.upsert_mentor(db, profile_dto)
        res_vo: MentorProfileVO = self.convert_to_mentor_profile_VO(res_dto, db)
        db.commit()
        return res_vo

    def get_profile_by_id(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        return self.convert_to_mentor_profile_VO(
            self.__mentor_repository.get_mentor_profile_by_id(db, mentor_profile_dto))

    def convert_to_mentor_profile_VO(self, dto: MentorProfileDTO, db: Session) -> MentorProfileVO:
        dic = dto.dict(exclude={"industry", "expertises", "skills", "topics"})
        res = MentorProfileVO(**dic)

        if (dto.skills is not None):
            res.skills = self.__interest_repository.get_interest_by_ids(db, dto.skills)
        if (dto.topics is not None):
            res.topics = self.__interest_repository.get_interest_by_ids(db, dto.topics)

        # res.user_id = dto.mentor_profile_id
        # res.industry = dto.industry
        return res
