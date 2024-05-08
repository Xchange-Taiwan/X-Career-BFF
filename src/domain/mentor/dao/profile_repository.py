from typing import List

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import MentorProfileDTO
from src.domain.user.model.user_model import ProfileDTO
from src.infra.db.orm.init.mentor_init import Profile
from src.infra.util.convert_util import convert_model_to_dto, convert_dto_to_model


class ProfileRepository:

    def get_all_profile(self, db: Session) -> List[ProfileDTO]:
        profiles = db.query(Profile).all()
        return [convert_model_to_dto(profile, ProfileDTO) for profile in profiles]

    def get_profiles_by_conditions(self, db: Session, dto: ProfileDTO) -> List[ProfileDTO]:
        dto_dict = dict(dto.__dict__)
        query = db.query(Profile)
        if dto_dict.get('user_id'):
            query = query.filter(Profile.user_id == dto.user_id)
            return [convert_model_to_dto(query.first(), ProfileDTO)]
        if dto_dict.get('name'):
            query = query.filter(Profile.name.like('%' + dto.name + '%'))

        if dto_dict.get('skills'):
            query = query.filter(
                func.cast(func.jsonb_array_elements_text(Profile.skills), Integer).any_(dto.skills)
            )
        if dto_dict.get('topics'):
            query = query.filter(
                func.cast(func.jsonb_array_elements_text(Profile.topics), Integer).any_(dto.topics)
            )
        profiles = query.all()
        return [convert_model_to_dto(profile, ProfileDTO) for profile in profiles]

    def upsert_profile(self, db: Session, dto: MentorProfileDTO) -> MentorProfileDTO:
        model = convert_dto_to_model(dto, Profile)
        db.merge(model)
        db.commit()
        return convert_model_to_dto(model, MentorProfileDTO)

    def delete_profile(self, db: Session, user_id: str) -> None:
        mentor = db.query(Profile).filter(Profile.user_id == user_id).first()
        if mentor:
            db.delete(mentor)
            db.commit()
