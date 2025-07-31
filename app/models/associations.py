from sqlalchemy import Table, Column, Integer, BigInteger, ForeignKey

from app.db.database import Base

appearance_type_relations = Table(
    'appearance_type_relations',
    Base.metadata,
    Column('appearance_id', BigInteger, ForeignKey('appearances.id'), primary_key=True),
    Column('appearance_type_id', Integer, ForeignKey('appearance_types.id'), primary_key=True)
)
