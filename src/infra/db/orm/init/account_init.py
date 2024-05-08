from sqlalchemy import Column, Integer, String, Boolean, types

from src.domain.account.enum.account_enum import AccountType
from src.infra.databse import Base


class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True)
    email1 = Column(String, nullable=False)
    email2 = Column(String)
    pass_hash = Column(String)
    pass_salt = Column(String)
    oauth_id = Column(String)
    refresh_token = Column(String)
    user_id = Column(String, unique=True)
    type = Column(types.Enum(AccountType))
    is_active = Column(Boolean)
    region = Column(String)
