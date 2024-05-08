from typing import List, Type, Optional

from sqlalchemy.orm import Session

from src.config.constant import IndustryCategory
from src.domain.mentor.dao.industry_repository import IndustryRepository
from src.domain.user.model.common_model import ProfessionListVO, ProfessionVO
from src.infra.db.orm.init.mentor_init import Industry


class IndustryService:
    def __init__(self, industry_repository: IndustryRepository):
        self.__industry_repository: IndustryRepository = industry_repository

    def get_all_industry(self, db: Session) -> ProfessionListVO:
        res: ProfessionListVO = ProfessionListVO()
        interests: List[Type[Industry]] = self.__industry_repository.get_all_industry(db)
        res.professions = [self.convert_to_profession_vo(interest) for interest in interests]
        return res

    def get_by_industry_category(self, db: Session, industry: IndustryCategory) -> ProfessionVO:
        return self.convert_to_profession_vo(
            self.__industry_repository.get_by_industry(db, industry))

    def convert_to_profession_vo(self, model: Optional[Type[Industry]]) -> ProfessionVO:
        res: ProfessionVO = ProfessionVO()
        if not model:
            return res

        res.metadata = model.metadata
        res.profession_category = model.profession_category
        res.subject = model.subject

        return res
