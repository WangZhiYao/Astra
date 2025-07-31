from sqlalchemy import Column, String, DateTime, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Appearance(Base):
    __tablename__ = "appearances"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    appearance_types = relationship(
        "AppearanceType",
        secondary="appearance_type_relations",
        back_populates="appearances"
    )
    appearance_aliases = relationship("AppearanceAlias", back_populates="appearance", cascade="all, delete-orphan")
    platform_relations = relationship("PlatformAppearanceRelation", back_populates="appearance")
    platform_price_histories = relationship("PlatformPriceHistory", back_populates="appearance")
