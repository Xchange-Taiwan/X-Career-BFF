from typing import List, Type, Optional

from sqlalchemy.orm import Session

from src.config.constant import ProfessionCategory
from src.config.exception import NotFoundException
from src.domain.mentor.dao.industry_repository import ProfessionRepository
from src.domain.user.model.common_model import ProfessionListVO, ProfessionVO
from src.infra.db.orm.init.user_init import Profession


class ProfessionService:
    def __init__(self, profession_repository: ProfessionRepository):
        self.__profession_repository: ProfessionRepository = profession_repository

    def get_all_profession(self, db: Session) -> ProfessionListVO:
        res: ProfessionListVO = ProfessionListVO()
        interests: List[Type[Profession]] = self.__profession_repository.get_all_profession(db)
        res.professions = [self.convert_to_profession_vo(interest) for interest in interests]
        return res

    def get_by_profession_category(self, db: Session, profession: ProfessionCategory) -> ProfessionVO:
        return self.convert_to_profession_vo(
            self.__profession_repository.get_by_profession(db, profession))

    def get_interest_by_ids(self, db: Session, ids: List[int]) -> ProfessionListVO:
        query: List[Type[Profession]] = db.query(Profession).filter(Profession.id.in_(ids)).all()
        res = [self.convert_to_profession_vo(profession) for profession in query]
        return ProfessionListVO(res)

    def get_interest_by_id(self, db: Session, id: int) -> ProfessionVO:
        query: Optional[Type[Profession]] = db.query(Profession).filter(Profession.id == id).first()

        return self.convert_to_profession_vo(query)

    def convert_to_profession_vo(self, dto: Optional[Type[Profession]]) -> ProfessionVO:
        if dto is None:
            raise NotFoundException(msg="no data found")
        res = ProfessionVO(**dict(dto.__dict__))

        return res
