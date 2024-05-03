from src.domain.mentor.mentor_repostory import MentorRepository
from src.domain.mentor.model.experties_repostory import ExpertisesRepository
from src.domain.mentor.model.mentor_model import MentorProfileDTO, MentorProfileVO


class MentorService:
    def __init__(self, mentor_repository: MentorRepository, expertises_repository: ExpertisesRepository):
        self.__mentor_repository: MentorRepository = mentor_repository
        self.__expertises_repository: ExpertisesRepository = expertises_repository

    def upsert_mentor(self, mentor_profile_dto: MentorProfileDTO) -> MentorProfileVO:
        res: MentorProfileVO = self.__mentor_repository.upsert_mentor(mentor_profile_dto)
        self.__expertises_repository.insert_inter_table(mentor_profile_dto)
        mentor_expertises_vo = self.__expertises_repository.get_by_mentor_id(mentor_profile_dto.id)
        res.expertises = mentor_expertises_vo
        return res

    def get_by_id(self, mentor_profile_dto):
        return self.__mentor_repository.get_mentor_by_id(mentor_profile_dto)
