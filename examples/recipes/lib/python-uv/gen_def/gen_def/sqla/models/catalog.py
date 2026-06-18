
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class Ingredient(Base):
    """
    A pantry ingredient type
    """
    __tablename__ = 'Ingredient'

    ingredient_type = Column(Text(), primary_key=True, nullable=False )
    name = Column(Text(), nullable=False )
    unit = Column(Text(), nullable=False )
    

    def __repr__(self):
        return f"Ingredient(ingredient_type={self.ingredient_type},name={self.name},unit={self.unit},)"



    


class Tool(Base):
    """
    A tool used to perform recipe steps (a PROV agent)
    """
    __tablename__ = 'Tool'

    tool_id = Column(Text(), primary_key=True, nullable=False )
    name = Column(Text(), nullable=False )
    

    def __repr__(self):
        return f"Tool(tool_id={self.tool_id},name={self.name},)"



    


class Recipe(Base):
    """
    A recipe header
    """
    __tablename__ = 'Recipe'

    recipe_id = Column(Text(), primary_key=True, nullable=False )
    name = Column(Text(), nullable=False )
    requires_type = Column(Text())
    output_type = Column(Text(), nullable=False )
    output_unit = Column(Text(), nullable=False )
    

    def __repr__(self):
        return f"Recipe(recipe_id={self.recipe_id},name={self.name},requires_type={self.requires_type},output_type={self.output_type},output_unit={self.output_unit},)"



    


class RecipeStep(Base):
    """
    One ordered, structured step of a recipe
    """
    __tablename__ = 'RecipeStep'

    id = Column(Text(), primary_key=True, nullable=False )
    recipe_id = Column(Text(), nullable=False )
    step_order = Column(Integer(), nullable=False )
    activity_kind = Column(Text(), nullable=False )
    tool_id = Column(Text())
    

    def __repr__(self):
        return f"RecipeStep(id={self.id},recipe_id={self.recipe_id},step_order={self.step_order},activity_kind={self.activity_kind},tool_id={self.tool_id},)"



    


class StepInput(Base):
    """
    One typed input consumed by a recipe step
    """
    __tablename__ = 'StepInput'

    id = Column(Text(), primary_key=True, nullable=False )
    recipe_id = Column(Text(), nullable=False )
    step_order = Column(Integer(), nullable=False )
    ingredient_type = Column(Text(), nullable=False )
    qty = Column(Integer(), nullable=False )
    unit = Column(Text(), nullable=False )
    

    def __repr__(self):
        return f"StepInput(id={self.id},recipe_id={self.recipe_id},step_order={self.step_order},ingredient_type={self.ingredient_type},qty={self.qty},unit={self.unit},)"



    


