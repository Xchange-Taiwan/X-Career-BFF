from typing import List

from sqlalchemy.orm import Session
from typing_extensions import Optional, Type

from src.config.constant import InterestCategory
from src.config.exception import NotFoundException
from src.domain.user.model.common_model import InterestVO
from src.infra.db.orm.init.user_init import Interest


class InterestRepository:
    def get_interest_by_ids(self, db: Session, ids: List[int]) -> List[Type[Interest]]:
        return db.query(Interest).filter(Interest.id.in_(ids)).all()

    def get_interest_by_id(self, db: Session, interest_id: int) -> Optional[Type[Interest]]:
        return db.query(Interest).filter(Interest.id == interest_id).first()

    def get_by_interest(self, db: Session, interest: InterestCategory) -> Optional[Type[Interest]]:
        return db.query(Interest).filter(Interest.category == interest).first()

    def get_all_interest(self, db: Session) -> List[Type[Interest]]:
        return db.query(Interest).all()
