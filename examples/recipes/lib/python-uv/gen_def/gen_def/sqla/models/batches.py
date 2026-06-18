
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class Batch(Base):
    """
    A durable running instance of a recipe
    """
    __tablename__ = 'Batch'

    id = Column(Text(), primary_key=True, nullable=False )
    recipe_id = Column(Text(), nullable=False )
    requires_type = Column(Text())
    status = Column(Text(), nullable=False )
    opened_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Batch(id={self.id},recipe_id={self.recipe_id},requires_type={self.requires_type},status={self.status},opened_at={self.opened_at},)"



    


