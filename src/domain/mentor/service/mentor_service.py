from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.mentor.dao.profession_repository import ProfessionRepository
from src.domain.mentor.dao.interest_repository import InterestRepository
from src.domain.mentor.dao.mentor_repository import MentorRepository
from src.domain.user.dao.profile_repository import ProfileRepository
from src.domain.mentor.model.mentor_model import MentorProfileDTO, MentorProfileVO
from src.domain.user.service.interest_service import InterestService
from src.domain.user.service.profession_service import ProfessionService


class MentorService:
    def __init__(self, mentor_repository: MentorRepository,
                 interest_service: InterestService,
                 profile_repository: ProfileRepository,
                 profession_service: ProfessionService):
        self.__mentor_repository: MentorRepository = mentor_repository
        self.__interest_service: InterestService = interest_service
        self.__profession_service: ProfessionService = profession_service
        self.__profile_repository = profile_repository

    async def upsert_mentor_profile(self, db: AsyncSession, profile_dto: MentorProfileDTO) -> MentorProfileVO:
        res_dto: MentorProfileDTO = await self.__mentor_repository.upsert_mentor(db, profile_dto)
        res_vo: MentorProfileVO = self.convert_to_mentor_profile_VO(db, res_dto)
        await db.commit()
        return res_vo

    async def get_mentor_profile_by_id(self, db: AsyncSession, mentor_profile_dto: MentorProfileDTO) -> MentorProfileVO:
        return self.convert_to_mentor_profile_VO(db,
                                                 await self.__mentor_repository.get_mentor_profile_by_id(db,
                                                                                                         mentor_profile_dto.user_id))

    def convert_to_mentor_profile_VO(self, db: AsyncSession, dto: MentorProfileDTO) -> MentorProfileVO:
        user_id = dto.user_id
        name = dto.name
        avatar = dto.avatar
        timezone = dto.timezone
        industry = self.__profession_service.get_profession_by_id(db, dto.industry)
        position = dto.position
        company = dto.company
        linkedin_profile = dto.linkedin_profile
        interested_positions = self.__interest_service.get_interest_by_ids(db, dto.interested_positions)
        skills = self.__interest_service.get_interest_by_ids(db, dto.industry)
        topics = self.__interest_service.get_interest_by_ids(db, dto.topics)
        location = dto.location
        personal_statement = dto.personal_statement
        about = dto.about
        seniority_level = dto.seniority_level
        experience = dto.experience
        expertises = self.__profession_service.get_profession_by_ids(db, dto.expertises)

        return MentorProfileVO(
            user_id=user_id,
            name=name,
            avatar=avatar,
            topics=topics,
            timezone=timezone,
            industry=industry,
            position=position,
            company=company,
            linkedin_profile=linkedin_profile,
            interested_positions=interested_positions,
            skills=skills,
            location=location,
            personal_statement=personal_statement,
            about=about,
            seniority_level=seniority_level,
            expertises=expertises,
            experience=experience

        )
