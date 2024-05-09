from typing import Optional, List

from sqlalchemy.orm import Session
from typing_extensions import Type

from src.config.constant import InterestCategory
from src.config.exception import NotFoundException
from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.user.model.common_model import InterestListVO, InterestVO
from src.infra.db.orm.init.user_init import Interest


class InterestService:
    def __init__(self, interest_repository: InterestRepository):
        self.__interest_repository: InterestRepository = interest_repository

    def get_all_interest(self, db: Session) -> InterestListVO:
        query: List[Type[Interest]] = self.__interest_repository.get_all_interest(db)

        interests: List[InterestVO] = [self.convert_to_interest_VO(interest) for interest in query]
        return InterestListVO(interests=interests)

    def get_by_interest_category(self, db: Session, interest: InterestCategory) -> InterestVO:
        return self.convert_to_interest_VO(self.__interest_repository.get_by_interest(db, interest))

    def get_interest_by_ids(self, db: Session, ids: List[int]) -> InterestListVO:
        query: List[Type[Interest]] = self.__interest_repository.get_interest_by_ids(db, ids)

        interests: List[InterestVO] = [self.convert_to_interest_VO(interest) for interest in query]
        return InterestListVO(interests=interests)

    def convert_to_interest_VO(self, dto: Optional[Type[Interest]]) -> InterestVO:
        if not dto:
            raise NotFoundException(msg="no data found")
        res = InterestVO(**dict(dto.__dict__))
        return res
