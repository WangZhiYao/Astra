from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class AppearanceType(Base):
    __tablename__ = "appearance_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

    appearances = relationship(
        "Appearance",
        secondary="appearance_type_relations",
        back_populates="appearance_types"
    )
