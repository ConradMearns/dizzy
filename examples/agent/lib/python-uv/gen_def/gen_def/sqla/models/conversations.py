
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class Message(Base):
    """
    One message row in a conversation, keyed by session_id.
    """
    __tablename__ = 'Message'

    id = Column(Text(), primary_key=True, nullable=False )
    session_id = Column(Text(), nullable=False )
    role = Column(Text(), nullable=False )
    content = Column(Text(), nullable=False )
    created_at = Column(DateTime(), nullable=False )
    prompt_tokens = Column(Integer())
    completion_tokens = Column(Integer())
    total_tokens = Column(Integer())
    cost_usd = Column(Float())
    

    def __repr__(self):
        return f"Message(id={self.id},session_id={self.session_id},role={self.role},content={self.content},created_at={self.created_at},prompt_tokens={self.prompt_tokens},completion_tokens={self.completion_tokens},total_tokens={self.total_tokens},cost_usd={self.cost_usd},)"



    


