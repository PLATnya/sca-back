from sqlalchemy import Column, Integer, String, Numeric
from database import Base


class Cat(Base):
    __tablename__ = "cats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    experience = Column(Integer, nullable=False)
    breed = Column(String(100), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)

