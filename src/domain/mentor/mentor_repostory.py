from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import Mentor, MentorProfileDTO
from src.infra.databse import get_db, Transaction


def convert_mentor_profile_dto(mentor: type[Mentor]) -> MentorProfileDTO:
    res = MentorProfileDTO()
    res.about = mentor.about
    res.seniority_level = mentor.seniority_level
    res.personal_statement = mentor.personal_statement
    return res


class MentorRepository:
    def __init__(self):
        self.db: Session = get_db()

    def get_all(self) -> List[MentorProfileDTO]:
        mentors = self.db.query(Mentor).all()
        return [convert_mentor_profile_dto(mentor) for mentor in mentors]

    def get_mentor_by_id(self, mentor_id: int) -> MentorProfileDTO:
        return convert_mentor_profile_dto(self.db.query(Mentor).filter(Mentor.id == mentor_id).first())

    def upsert_mentor(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileDTO:
        res: MentorProfileDTO = MentorProfileDTO()

        mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_profile_dto.id).first()

        if mentor:
            mentor.personal_statement = mentor_profile_dto.personal_statement
            mentor.seniority_level = mentor_profile_dto.seniority_level
            mentor.about = mentor_profile_dto.about
            db.add(mentor)
            res = convert_mentor_profile_dto(mentor)
        else:
            mentor = Mentor()
            mentor.about = mentor_profile_dto.about
            mentor.seniority_level = mentor_profile_dto.seniority_level
            mentor.personal_statement = mentor_profile_dto.personal_statement
            db.add(mentor)
            db.commit()
            db.refresh(mentor)
            res = convert_mentor_profile_dto(mentor)
        return res

    def delete_mentor_by_id(self, mentor_id: int) -> None:
        mentor = self.db.query(Mentor).filter_by(Mentor.mentor_id == mentor_id).first()
        if mentor:
            self.db.delete(mentor)
            self.db.commit()
