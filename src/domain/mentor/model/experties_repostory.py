from typing import List

from sqlalchemy.orm import Session

from src.config.constant import ProfessionCategory
from src.domain.mentor.model.mentor_model import MentorExpertisesVo, MentorExpertisesInter, MentorExpertises, Mentor, \
    MentorProfileDTO
from src.domain.user.model.common_model import ProfessionListVO, ProfessionVO
from src.infra.databse import Transaction


def convert_to_profession_vo(mentor_expert: type[MentorExpertises]) -> ProfessionVO:
    vo = ProfessionVO()
    if not mentor_expert:
        return vo

    vo.id = mentor_expert.expertises_id
    vo.subject = mentor_expert.subject
    vo.metadata = {}
    vo.category = ProfessionCategory.EXPERTISE
    return vo


def convert_to_mentor_expertises_vo(mentor_expert: type[MentorExpertises]) -> MentorExpertisesVo:
    vo = MentorExpertisesVo()
    if not mentor_expert:
        return vo

    vo.expertises_id = mentor_expert.expertises_id
    vo.expertises = mentor_expert.expertises
    vo.industry = mentor_expert.industry
    vo.subject = mentor_expert.subject
    return vo


class ExpertisesRepository:
    def get_all(self) -> List[MentorExpertisesVo]:
        mentor_experts: List[type[MentorExpertises]] = self.db.query(MentorExpertises).all()
        return [convert_to_mentor_expertises_vo(res) for res in mentor_experts]

    def get_by_mentor_id(self, mentor_id: int, db: Session) -> List[MentorExpertisesVo]:
        mentor_expert_list: List[type[MentorExpertises]] = ((db.query(MentorExpertises)
                                                             .join(MentorExpertisesInter)
                                                             .filter(
            MentorExpertisesInter.mentor_id == mentor_id
            and MentorExpertisesInter.expertises_id == MentorExpertises.expertises_id)
                                                             .join(Mentor)
                                                             .filter(Mentor.mentor_id == mentor_id))

                                                            .all())

        return [convert_to_mentor_expertises_vo(res) for res in mentor_expert_list]

    def insert_inter_table(self, mentor_dto: MentorProfileDTO, db: Session) -> list[MentorExpertisesInter]:
        insert_list: list[MentorExpertisesInter] = []

        for expert in mentor_dto.expertises:
            inter = MentorExpertisesInter()
            inter.expertises_id = expert.id
            inter.mentor_id = mentor_dto.id
            insert_list.append(inter)
        db.add_all(insert_list)

        return insert_list
