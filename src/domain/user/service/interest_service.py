from typing import Optional, List

from sqlalchemy.orm import Session
from typing_extensions import Type

from src.config.constant import InterestCategory
from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.user.model.common_model import InterestListVO, InterestVO
from src.infra.db.orm.init.mentor_init import Interest


class InterestService:
    def __init__(self, interest_repository: InterestRepository):
        self.__interest_repository: InterestRepository = interest_repository

    def get_all_interest(self, db: Session) -> InterestListVO:
        res: InterestListVO = InterestListVO()
        interests: List[Type[Interest]] = self.__interest_repository.get_all_interest(db)
        res.interests = [self.convert_to_interest_VO(interest) for interest in interests]
        return res

    def get_by_interest_category(self, db: Session, interest: InterestCategory) -> InterestListVO:
        res : InterestListVO = InterestListVO()
        res.interests = [self.convert_to_interest_VO(
            self.__interest_repository.get_by_interest(db, interest))]
        return res

    def convert_to_interest_VO(self, dto: Optional[Type[Interest]]) -> InterestVO:
        res: InterestVO = InterestVO()
        if not dto:
            return res

        res.category = dto.category
        res.subject = dto.subject
        res.desc = dto.desc
        return res
