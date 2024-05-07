from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base


# model 跟 dto 互轉的方法們，如果有需求請override
def convert_model_to_dto(model_class: type[declarative_base], dto_class: object):
    return dto_class.parse_obj(dict(model_class.__dict__))


def convert_dto_to_model(dto: BaseModel, model_class: declarative_base, exclude: set = {}):
    return model_class(**dto.dict(exclude=exclude))
