from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine

from sqlalchemy import Column, Integer, VARCHAR, DATE

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    # telegram user_id
    user_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    # telegram user_id
    user_name = Column(VARCHAR(32), unique=False, nullable=False)

    def __str__(self) -> str:
        return f"<User:(self_id)>"
