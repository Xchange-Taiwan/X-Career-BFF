from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import Interests


class InterestRepository:
    def get_interest_by_ids(self, ids: List[int], db: Session):
        return db.query(Interests).filter(Interests.id.in_(ids)).all()
