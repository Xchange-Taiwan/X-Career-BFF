from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import MentorProfile, MentorProfileDTO


def convert_mentor_profile_dto(mentor: type[MentorProfile]) -> MentorProfileDTO:
    res = MentorProfileDTO()
    if mentor:
        for key, value in mentor.__dict__.items():
            if value is not None:
                try:
                    setattr(res, key, value)
                except (AttributeError, ValueError) as err:
                    print("key not in dto", key)
    return res


class MentorRepository:

    def get_all_mentor_profile(self, db: Session) -> List[MentorProfileDTO]:
        mentors = db.query(MentorProfile).all()
        return [convert_mentor_profile_dto(mentor) for mentor in mentors]

    def get_mentor_profile_by_id(self, mentor_id: int, db: Session) -> MentorProfileDTO:
        return convert_mentor_profile_dto(db.query(MentorProfile).filter(MentorProfile.id == mentor_id).first())

    def upsert_mentor(self, mentor_profile_dto: MentorProfileDTO, db: Session) -> MentorProfileDTO:
        res: MentorProfileDTO = MentorProfileDTO()

        mentor = db.query(MentorProfile).filter(MentorProfile.mentor_profile_id == mentor_profile_dto.mentor_profile_id).first()

        if not mentor:
            mentor = MentorProfile()

        for key, value in mentor_profile_dto.__dict__.items():
            if value is not None:
                setattr(mentor, key, value)
        db.add(mentor)
        res = convert_mentor_profile_dto(mentor)
        db.commit()
        return res

    def delete_mentor_profile_by_id(self, mentor_profile_id: int) -> None:
        mentor = self.db.query(MentorProfile).filter_by(MentorProfile.mentor_id == mentor_profile_id).first()
        if mentor:
            self.db.delete(mentor)
            self.db.commit()
