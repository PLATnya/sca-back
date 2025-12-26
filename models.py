from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey
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
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    notes = Column(Text, nullable=False)
    complete_state = Column(Boolean, nullable=False, default=False)


class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey('cats.id'), nullable=True, index=True)
    complete_state = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    cat = relationship("Cat", backref="missions")
    targets = relationship("Target", backref="mission", cascade="all, delete-orphan")

