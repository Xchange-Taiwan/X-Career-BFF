from typing import List

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import MentorProfileDTO
from src.infra.db.orm.init.user_init import Profile, MentorExperience
from src.infra.util.convert_util import convert_model_to_dto, convert_dto_to_model


class MentorRepository:

    def get_all_mentor_profile(self, db: Session) -> List[MentorProfileDTO]:
        mentors = db.query(Profile).all()
        return [convert_model_to_dto(mentor, MentorProfileDTO) for mentor in mentors]

    def get_mentor_profile_by_id(self, db: Session, mentor_id: int) -> MentorProfileDTO:

        #join MentorExperience 有存在的才返回
        return convert_model_to_dto(
            db.query(Profile).join(MentorExperience, MentorExperience.user_id == Profile.user_id).filter(
                Profile.user_id == mentor_id).first(),
            MentorProfileDTO)

    def get_mentor_profiles_by_conditions(self, db: Session, dto: MentorProfileDTO) -> List[MentorProfileDTO]:
        dto_dict = dict(dto.__dict__)
        query = db.query(Profile)
        if dto_dict.get('name'):
            query = query.filter(Profile.name == dto.name)
        if dto_dict.get('location'):
            query = query.filter(Profile.location.like('%' + dto.location + '%'))
        if dto_dict.get('about'):
            query = query.filter(Profile.about.like('%' + dto.about + '%'))
        if dto_dict.get('personal_statement'):
            query = query.filter(Profile.about.like('%' + dto.personal_statement + '%'))
        if dto_dict.get('seniority_level'):
            query = query.filter(Profile.seniority_level == dto.seniority_level)
        if dto_dict.get('industry'):
            query = query.filter(Profile.industry == dto.industry)
        if dto_dict.get('position'):
            query = query.filter(Profile.position == dto.position)
        if dto_dict.get('company'):
            query = query.filter(Profile.company == dto.company)
        if dto_dict.get('experience'):
            query = query.filter(Profile.experience >= dto.experience)

        if dto_dict.get('skills'):
            query = query.filter(
                func.cast(func.jsonb_array_elements_text(Profile.skills), Integer).any_(dto.skills)
            )
        if dto_dict.get('topics'):
            query = query.filter(
                func.cast(func.jsonb_array_elements_text(Profile.topics), Integer).any_(dto.topics)
            )
        if dto_dict.get('expertises'):
            query = query.filter(
                func.cast(func.jsonb_array_elements_text(Profile.expertises), Integer).any_(dto.expertises)
            )
        profiles = query.all()
        return [convert_model_to_dto(profile, MentorProfileDTO) for profile in profiles]

    def upsert_mentor(self, db: Session, mentor_profile_dto: MentorProfileDTO) -> MentorProfileDTO:
        mentor = convert_dto_to_model(mentor_profile_dto, Profile)
        db.merge(mentor)
        res = convert_model_to_dto(mentor, MentorProfileDTO)

        return res

    def delete_mentor_profile_by_id(self, db: Session, user_id: int) -> None:
        mentor = db.query(Profile).filter(Profile.user_id == user_id).first()
        if mentor:
            db.delete(mentor)
            db.commit()
