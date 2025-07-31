from sqlalchemy import Column, BigInteger, ForeignKey, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class UserSaleTransaction(Base):
    __tablename__ = "user_sale_transactions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    appearance_id = Column(BigInteger, ForeignKey('appearances.id'), nullable=False)
    platform_id = Column(Integer, ForeignKey('platforms.id'))
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(BigInteger, nullable=False)
    platform_fee_cents = Column(BigInteger, nullable=False, default=0)
    sold_at = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="sale_transactions")
    appearance = relationship("Appearance")
    platform = relationship("Platform")
