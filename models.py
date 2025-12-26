from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base


class Cat(Base):
    __tablename__ = "cats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    experience = Column(Integer, nullable=False)
    breed = Column(String(100), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)


class Target(Base):
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    notes = Column(Text, nullable=False)
    complete_state = Column(Boolean, nullable=False, default=False)


# Junction table for many-to-many relationship between Mission and Target
mission_target = Table(
    'mission_target',
    Base.metadata,
    Column('mission_id', Integer, ForeignKey('missions.id'), primary_key=True),
    Column('target_id', Integer, ForeignKey('targets.id'), primary_key=True)
)


class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey('cats.id'), nullable=False, index=True)
    complete_state = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    cat = relationship("Cat", backref="missions")
    targets = relationship("Target", secondary=mission_target, backref="missions")

