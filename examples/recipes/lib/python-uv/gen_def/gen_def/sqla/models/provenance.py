
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class ProvGeneration(Base):
    """
    An entity and the activity/batch that generated it (prov:wasGeneratedBy)
    """
    __tablename__ = 'ProvGeneration'

    entity_id = Column(Text(), primary_key=True, nullable=False )
    entity_type = Column(Text(), nullable=False )
    batch_id = Column(Text(), nullable=False )
    activity_id = Column(Text(), nullable=False )
    produced_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"ProvGeneration(entity_id={self.entity_id},entity_type={self.entity_type},batch_id={self.batch_id},activity_id={self.activity_id},produced_at={self.produced_at},)"



    


class ProvDerivation(Base):
    """
    A derivation edge linking an output entity to its source (prov:wasDerivedFrom)
    """
    __tablename__ = 'ProvDerivation'

    output_entity_id = Column(Text(), primary_key=True, nullable=False )
    source_entity_id = Column(Text(), nullable=False )
    

    def __repr__(self):
        return f"ProvDerivation(output_entity_id={self.output_entity_id},source_entity_id={self.source_entity_id},)"



    


