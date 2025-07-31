from sqlalchemy.orm import Session

from app.models import AppearanceType
from app.schemas import AppearanceTypeCreate


def get_appearance_type_by_name(db: Session, name: str):
    return db.query(AppearanceType).filter(AppearanceType.name == name).first()


def create_appearance_type(db: Session, appearance_type: AppearanceTypeCreate):
    db_appearance_type = AppearanceType(
        name=appearance_type.name
    )
    db.add(db_appearance_type)
    db.commit()
    db.refresh(db_appearance_type)
    return db_appearance_type
