from sqlalchemy.orm import Session

from app.models import Appearance
from app.schemas import AppearanceCreate


def get_appearance_by_name(db: Session, name: str):
    return db.query(Appearance).filter(Appearance.name == name).first()


def create_appearance(db: Session, appearance: AppearanceCreate):
    db_appearance = Appearance(
        name=appearance.name,
        description=appearance.description,
        image_url=appearance.image_url
    )
    db.add(db_appearance)
    db.commit()
    db.refresh(db_appearance)
    return db_appearance
