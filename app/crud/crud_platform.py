from sqlalchemy.orm import Session

from app.models import Platform
from app.schemas import PlatformCreate


def get_platform_by_name(db: Session, name: str):
    return db.query(Platform).filter(Platform.name == name).first()


def create_platform(db: Session, platform: PlatformCreate):
    db_platform = Platform(
        name=platform.name
    )
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform
