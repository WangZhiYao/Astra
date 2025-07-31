from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class PlatformAppearanceRelation(Base):
    __tablename__ = "platform_appearance_relations"

    platform_id = Column(Integer, ForeignKey('platforms.id'), primary_key=True)
    appearance_id = Column(BigInteger, ForeignKey('appearances.id'), primary_key=True)
    platform_appearance_id = Column(String(255), nullable=False, primary_key=True)

    platform = relationship("Platform", back_populates="appearance_relations")
    appearance = relationship("Appearance", back_populates="platform_relations")
