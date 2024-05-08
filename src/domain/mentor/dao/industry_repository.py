from typing import List, Optional, Type

from sqlalchemy.orm import Session

from src.config.constant import IndustryCategory
from src.infra.db.orm.init.mentor_init import Industry


class IndustryRepository:
    def get_interest_by_ids(self, db: Session, ids: List[int]):
        return db.query(Industry).filter(Industry.id.in_(ids)).all()

    def get_interest_by_id(self, db: Session, industry_id: int):
        return db.query(Industry).filter(Industry.id == industry_id).first()

    def get_by_industry(self, db: Session, category: IndustryCategory) -> Optional[Type[Industry]]:
        return db.query(Industry).filter(Industry.profession_category == category).first()

    def get_all_industry(self, db: Session) -> List[Type[Industry]]:
        return db.query(Industry).all()
