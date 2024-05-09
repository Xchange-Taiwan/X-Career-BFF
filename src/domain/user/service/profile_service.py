from typing import List, Optional, Dict

from sqlalchemy.orm import Session

from src.config.exception import NotAcceptableException, NotFoundException
from src.domain.user.dao.profile_repository import ProfileRepository
from src.domain.user.model.common_model import ProfessionVO, InterestListVO
from src.domain.user.model.user_model import ProfileDTO, ProfileVO
from src.domain.user.service.interest_service import InterestService
from src.domain.user.service.profession_service import ProfessionService


class ProfileService:
    def __init__(self,
                 interest_service: InterestService,
                 profile_repository: ProfileRepository,
                 profession_service: ProfessionService):
        self.__interest_service: InterestService = interest_service
        self.__profession_service: ProfessionService = profession_service
        self.__profile_repository = profile_repository

    def get_by_user_id(self, db: Session, user_id: int) -> ProfileVO:
        if user_id is None:
            raise NotAcceptableException(msg="No user id is provided")

        return self.convert_to_profile_vo(self.__profile_repository.get_by_user_id(db, user_id))

    def get_by_conditions(self, db: Session, dto: ProfileDTO) -> List[ProfileDTO]:
        return self.__profile_repository.get_profiles_by_conditions(db, dto)

    def upsert_profile(self, db: Session, dto: ProfileDTO) -> ProfileVO:
        return self.convert_to_profile_vo(db, self.__profile_repository.upsert_profile(db, dto))

    def convert_to_profile_vo(self, db: Session, dto: ProfileDTO) -> ProfileVO:
        if dto is None:
            raise NotFoundException(msg="no data found")
        industry: Optional[ProfessionVO] = self.__profession_service.get_interest_by_id(db, dto.industry)
        interested_positions: Optional[InterestListVO] = self.__interest_service.get_interest_by_ids(db,
                                                                                                     dto.interested_positions)
        skills: Optional[InterestListVO] = self.__interest_service.get_interest_by_ids(db, dto.skills)
        topics: Optional[InterestListVO] = self.__interest_service.get_interest_by_ids(db, dto.topics)

        return ProfileVO(
            user_id=dto.user_id,
            name=dto.name,
            avatar=dto.avatar,
            timezone=dto.timezone,
            industry=industry,
            position=dto.position,
            company=dto.company,
            linkedin_profile=dto.linkedin_profile,
            interested_positions=interested_positions,
            skills=skills,
            topics=topics
        )
