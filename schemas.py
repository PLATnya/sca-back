from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class CatBase(BaseModel):
    name: str
    experience: int
    breed: str
    salary: Decimal


class CatCreate(CatBase):
    pass


class CatUpdate(BaseModel):
    salary: Decimal


class CatResponse(CatBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

