
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class InventoryEntity(Base):
    """
    A produced entity lot
    """
    __tablename__ = 'InventoryEntity'

    id = Column(Text(), primary_key=True, nullable=False )
    entity_type = Column(Text(), nullable=False )
    qty = Column(Integer(), nullable=False )
    unit = Column(Text(), nullable=False )
    batch_id = Column(Text(), nullable=False )
    available = Column(Boolean(), nullable=False )
    

    def __repr__(self):
        return f"InventoryEntity(id={self.id},entity_type={self.entity_type},qty={self.qty},unit={self.unit},batch_id={self.batch_id},available={self.available},)"



    


