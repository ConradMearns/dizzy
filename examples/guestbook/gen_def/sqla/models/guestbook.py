
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class Signature(Base):
    """
    A single stored guestbook signature
    """
    __tablename__ = 'Signature'

    id = Column(Text(), primary_key=True, nullable=False )
    visitor_name = Column(Text(), nullable=False )
    message = Column(Text(), nullable=False )
    signed_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Signature(id={self.id},visitor_name={self.visitor_name},message={self.message},signed_at={self.signed_at},)"



    


