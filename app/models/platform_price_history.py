from sqlalchemy import Column, BigInteger, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class PlatformPriceHistory(Base):
    __tablename__ = "platform_price_history"

    id = Column(BigInteger, primary_key=True, index=True)
    appearance_id = Column(BigInteger, ForeignKey('appearances.id'), nullable=False)
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False)
    lowest_price_cents = Column(BigInteger, nullable=False)
    quantity_on_sale = Column(Integer)
    crawled_at = Column(DateTime(timezone=True), nullable=False)

    appearance = relationship("Appearance", back_populates="platform_price_histories")
    platform = relationship("Platform")
