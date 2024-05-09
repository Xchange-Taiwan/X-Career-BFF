from typing import List, Optional, Type

from sqlalchemy.orm import Session

from src.config.constant import ProfessionCategory
from src.infra.db.orm.init.user_init import Profession


class ProfessionRepository:
    def get_profession_by_ids(self, db: Session, ids: List[int]):
        return db.query(Profession).filter(Profession.id.in_(ids)).all()

    def get_profession_by_id(self, db: Session, industry_id: int):
        return db.query(Profession).filter(Profession.id == industry_id).first()

    def get_by_profession(self, db: Session, category: ProfessionCategory) -> Optional[Type[Profession]]:
        return db.query(Profession).filter(Profession.category == category).first()

    def get_all_profession(self, db: Session) -> List[Type[Profession]]:
        return db.query(Profession).all()
