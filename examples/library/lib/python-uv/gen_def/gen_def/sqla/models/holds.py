
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class Hold(Base):
    """
    A single active hold in the queue
    """
    __tablename__ = 'Hold'

    id = Column(Text(), primary_key=True, nullable=False )
    book_id = Column(Text(), nullable=False )
    patron = Column(Text(), nullable=False )
    placed_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Hold(id={self.id},book_id={self.book_id},patron={self.patron},placed_at={self.placed_at},)"



    


