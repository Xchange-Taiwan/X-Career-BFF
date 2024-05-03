from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import Mentor, MentorProfileDTO, MentorProfileVO
from src.infra.databse import get_db, Transaction


def convert_mentor_profile_vo(mentor: type[Mentor]) -> MentorProfileVO:
    res = MentorProfileVO()
    res.about = mentor.about
    res.seniority_level = mentor.seniority_level
    res.personal_statement = mentor.personal_statement
    return res


class MentorRepository:
    def __init__(self):
        self.db: Session = get_db()

    def get_all(self) -> List[MentorProfileVO]:
        mentors = self.db.query(Mentor).all()
        return [convert_mentor_profile_vo(mentor) for mentor in mentors]

    def get_mentor_by_id(self, mentor_id: int) -> MentorProfileVO:
        return convert_mentor_profile_vo(self.db.query(Mentor).filter(Mentor.id == mentor_id).first())

    def upsert_mentor(self, mentor_profile_dto: MentorProfileDTO) -> MentorProfileVO:
        with Transaction() as session:
            mentor = self.db.query(Mentor).filter_by(id=mentor_profile_dto.id).first()
            res: MentorProfileVO = MentorProfileVO()
            if mentor:
                mentor.personal_statement = mentor_profile_dto.personal_statement
                mentor.seniority_level = mentor_profile_dto.seniority_level
                mentor.about = mentor_profile_dto.about
                res = convert_mentor_profile_vo(mentor)
            else:
                mentor = Mentor()
                mentor.about = mentor_profile_dto.about
                mentor.seniority_level = mentor_profile_dto.seniority_level
                mentor.personal_statement = mentor_profile_dto.personal_statement
            return res

    def delete_mentor_by_id(self, mentor_id: int) -> None:
        mentor = self.db.query(Mentor).filter_by(id=mentor_id).first()
        if mentor:
            self.db.delete(mentor)
            self.db.commit()
