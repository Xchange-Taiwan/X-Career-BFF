from typing import List

from sqlalchemy.orm import Session

from src.domain.mentor.model.mentor_model import MentorExpertisesVo, MentorExpertisesInter, MentorExpertises, Mentor, \
    MentorProfileDTO
from src.infra.databse import Transaction


def convert(mentor_expert: type[MentorExpertises]) -> MentorExpertisesVo:
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
        return [convert(res) for res in mentor_experts]

    def get_by_mentor_id(self, mentor_id: int, db: Session) -> List[MentorExpertisesVo]:
        mentor_expert_list: List[type[MentorExpertises]] = ((db.query(MentorExpertises)
                                                             .join(MentorExpertisesInter)
                                                             .filter(
            MentorExpertisesInter.mentor_id == mentor_id
            and MentorExpertisesInter.expertises_id == MentorExpertises.expertises_id)
                                                             .join(Mentor)
                                                             .filter(Mentor.mentor_id == mentor_id))

                                                            .all())

        return [convert(res) for res in mentor_expert_list]

    def insert_inter_table(self, mentor_dto: MentorProfileDTO) -> list[MentorExpertisesInter]:
        insert_list: list[MentorExpertisesInter] = []

        for expert in mentor_dto.expertises:
            inter = MentorExpertisesInter()
            inter.expertises_id = expert.id
            inter.mentor_id = mentor_dto.id
            insert_list.append(inter)
        with Transaction() as session:
            session.add_all(insert_list)

        return insert_list
