from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class AppearanceAlias(Base):
    __tablename__ = "appearance_aliases"

    id = Column(BigInteger, primary_key=True, index=True)
    appearance_id = Column(BigInteger, ForeignKey('appearances.id'), nullable=False)
    alias_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    appearance = relationship("Appearance", back_populates="appearance_aliases")
