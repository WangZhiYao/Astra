from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm import joinedload

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus
from app.core.paging import PagingData


def _get_appearance_by_name(db: Session, name: str) -> Optional[models.Appearance]:
    return db.query(models.Appearance).filter(models.Appearance.name == name).first()


def create_appearance(db: Session, appearance: schemas.AppearanceCreate) -> OperationResult[schemas.Appearance]:
    db_appearance = _get_appearance_by_name(db=db, name=appearance.name)
    if db_appearance:
        return OperationResult(
            status=OperationStatus.CONFLICT,
            data=schemas.Appearance.model_validate(db_appearance)
        )

    db_appearance = models.Appearance(
        name=appearance.name,
        description=appearance.description,
        image_url=appearance.image_url
    )

    db.add(db_appearance)
    db.commit()
    db.refresh(db_appearance)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Appearance.model_validate(db_appearance))


def get_appearance_by_id(db: Session, appearance_id: int) -> OperationResult[schemas.Appearance]:
    db_appearance = db.query(models.Appearance).options(
        joinedload(models.Appearance.appearance_aliases),
        joinedload(models.Appearance.appearance_types)
    ).filter(models.Appearance.id == appearance_id).first()

    if not db_appearance:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Appearance.model_validate(db_appearance))


def get_appearances(
        db: Session,
        page: int = 1,
        page_size: int = 100,
        search_query: Optional[str] = None
) -> OperationResult[PagingData[schemas.Appearance]]:
    # 基础查询，包含所有过滤条件
    base_query = db.query(models.Appearance.id)  # 仅选择 ID 以提高效率

    if search_query:
        # 使用 join 替代 any()，这在某些情况下对 count 更友好
        # 注意：这里需要明确 join，因为我们只 select ID
        base_query = (
            base_query.outerjoin(models.Appearance.appearance_aliases)
            .filter(
                (models.Appearance.name.ilike(f"%{search_query}%")) |
                (models.AppearanceAlias.alias_name.ilike(f"%{search_query}%"))
            )
        )

    # 1. 计算总数 (在应用分页前)
    # 使用 count(distinct) 来确保在 JOIN 后计数正确
    subquery = base_query.distinct().subquery()
    total_count = db.query(func.count()).select_from(subquery).scalar()

    if total_count == 0:
        return OperationResult(
            status=OperationStatus.SUCCESS,
            data=PagingData(items=[], total_count=0)
        )

    # 2. 获取当前页的 Appearance IDs
    offset = (page - 1) * page_size

    appearance_ids_on_page = (
        base_query
        .distinct()  # 确保每个 Appearance ID 只出现一次
        .order_by(models.Appearance.id)  # 稳定的分页需要 order_by
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 从元组列表中提取 IDs: [(id1,), (id2,)] -> [id1, id2]
    ids = [item[0] for item in appearance_ids_on_page]

    if not ids:
        # 如果计算出的 IDs 为空（可能发生在页码超出范围时），直接返回
        return OperationResult(
            status=OperationStatus.SUCCESS,
            data=PagingData(items=[], total_count=total_count)
        )

    # 3. 根据 IDs 获取完整的 Appearance 对象，并预加载关联数据
    # 这是唯一需要加载完整对象和关联数据的地方
    db_appearances = (
        db.query(models.Appearance)
        .filter(models.Appearance.id.in_(ids))
        .options(
            selectinload(models.Appearance.appearance_aliases),
            selectinload(models.Appearance.appearance_types)
        )
        .order_by(models.Appearance.id)  # 保持与 ID 查询相同的顺序
        .all()
    )

    items = [schemas.Appearance.model_validate(db_appearance) for db_appearance in db_appearances]

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=PagingData(items=items, total_count=total_count)
    )


def update_appearance(
        db: Session,
        appearance_id: int,
        appearance: schemas.AppearanceUpdate
) -> OperationResult[schemas.Appearance]:
    db_appearance = db.query(models.Appearance).filter(models.Appearance.id == appearance_id).first()
    if not db_appearance:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = appearance.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_appearance.name:
        existing_appearance = _get_appearance_by_name(db, name=update_data["name"])
        if existing_appearance:
            return OperationResult(status=OperationStatus.CONFLICT,
                                   data=schemas.Appearance.model_validate(existing_appearance))

    for key, value in update_data.items():
        setattr(db_appearance, key, value)
    db.add(db_appearance)
    db.commit()
    db.refresh(db_appearance)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Appearance.model_validate(db_appearance))


def delete_appearance(db: Session, appearance_id: int) -> OperationResult:
    db_appearance = db.query(models.Appearance).filter(models.Appearance.id == appearance_id).first()
    if not db_appearance:
        return OperationResult(status=OperationStatus.NOT_FOUND)
    db.delete(db_appearance)
    db.commit()
    return OperationResult(status=OperationStatus.SUCCESS)
