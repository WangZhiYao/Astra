from sqlalchemy import Column, BigInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(BigInteger, primary_key=True, index=True)
    watchlist_id = Column(BigInteger, ForeignKey('watchlists.id'), nullable=False)
    appearance_id = Column(BigInteger, ForeignKey('appearances.id'), nullable=False)
    target_price_cents = Column(BigInteger, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    watchlist = relationship("Watchlist", back_populates="items")
    appearance = relationship("Appearance")
