from typing import List, Optional, Type

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

from src.config.exception import NotFoundException
from src.domain.mentor.model.mentor_model import MentorProfileDTO
from src.domain.user.model.user_model import ProfileDTO
from src.infra.db.orm.init.user_init import Profile
from src.infra.util.convert_util import convert_model_to_dto, convert_dto_to_model


class ProfileRepository:

    def get_all_profile(self, db: Session) -> List[ProfileDTO]:
        profiles = db.query(Profile).all()
        return [convert_model_to_dto(profile, ProfileDTO) for profile in profiles]

    def get_by_user_id(self, db: Session, user_id: int) -> ProfileDTO:
        query: Optional[Type[Profile]] = db.query(Profile).filter(Profile.user_id == user_id).first()
        if query is None:
            raise NotFoundException(msg=f"No such user with id: {user_id}")
        return convert_model_to_dto(query, ProfileDTO)

    def get_profiles_by_conditions(self, db: Session, dto: ProfileDTO) -> List[ProfileDTO]:
        dto_dict = dict(dto.__dict__)
        query = db.query(Profile)

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

    def upsert_profile(self, db: Session, dto: ProfileDTO) -> ProfileDTO:
        # model = self.convert_dto_to_profile(dto)
        model = convert_dto_to_model(dto, Profile)
        db.merge(model)
        db.commit()
        return convert_model_to_dto(model, ProfileDTO)

    def delete_profile(self, db: Session, user_id: str) -> None:
        mentor = db.query(Profile).filter(Profile.user_id == user_id).first()
        if mentor:
            db.delete(mentor)
            db.commit()

    def convert_dto_to_profile(self, dto: ProfileDTO) -> Profile:
        profile: Profile = Profile()
        profile.user_id: Optional[int] = dto.user_id
        profile.name: Optional[str] = dto.name
        profile.avatar: Optional[str] = dto.avatar
        profile.timezone: Optional[int] = dto.timezone
        profile.industry: Optional[int] = dto.industry
        profile.position: Optional[str] = dto.position
        profile.company: Optional[str] = dto.company
        profile.linkedin_profile: Optional[str] = dto.linkedin_profile
        profile.interested_positions: Optional[List[int]] = dto.interested_positions
        profile.skills: Optional[List[int]] = dto.skills
        profile.topics: Optional[List[int]] = dto.topics
        return profile
