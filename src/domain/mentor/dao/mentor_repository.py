from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import MentorProfile, MentorProfileDTO, MentorProfileVO
from src.infra.util.convert_util import convert_model_to_dto, convert_dto_to_model


class MentorRepository:

    def get_all_mentor_profile(self, db: Session) -> List[MentorProfileDTO]:
        mentors = db.query(MentorProfile).all()
        return [convert_model_to_dto(mentor) for mentor in mentors]

    def get_mentor_profile_by_id(self, mentor_id: int, db: Session) -> MentorProfileDTO:
        return convert_model_to_dto(db.query(MentorProfile).filter(MentorProfile.id == mentor_id).first())

    def upsert_mentor(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileDTO:
        mentor = convert_dto_to_model(mentor_profile_dto, MentorProfile)
        db.merge(mentor)
        res = convert_model_to_dto(mentor, MentorProfileDTO)

        return res

    def delete_mentor_profile_by_id(self, mentor_profile_id: int) -> None:
        mentor = self.db.query(MentorProfile).filter_by(MentorProfile.mentor_id == mentor_profile_id).first()
        if mentor:
            self.db.delete(mentor)
            self.db.commit()
