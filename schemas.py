from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from typing import List, Optional


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


class TargetBase(BaseModel):
    name: str
    country: str
    notes: str
    complete_state: bool


class TargetCreate(TargetBase):
    pass


class TargetResponse(TargetBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class TargetInMission(BaseModel):
    name: str
    country: str
    notes: str = ""


class MissionCreate(BaseModel):
    targets: List[TargetInMission] = Field(..., min_length=1, max_length=3)
    
    @field_validator('targets')
    @classmethod
    def validate_target_count(cls, v):
        if len(v) < 1 or len(v) > 3:
            raise ValueError('Mission must have between 1 and 3 targets')
        return v


class MissionAssignCat(BaseModel):
    cat_id: int


class MissionUpdateTargets(BaseModel):
    targets: List[TargetInMission] = Field(..., min_length=1, max_length=3)
    
    @field_validator('targets')
    @classmethod
    def validate_target_count(cls, v):
        if len(v) < 1 or len(v) > 3:
            raise ValueError('Mission must have between 1 and 3 targets')
        return v


class MissionUpdateNotes(BaseModel):
    notes: str


class MissionResponse(BaseModel):
    id: int
    cat_id: Optional[int]
    targets: List[TargetResponse]
    complete_state: bool
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, mission):
        """Custom method to convert Mission model to response"""
        return cls(
            id=mission.id,
            cat_id=mission.cat_id,
            targets=[TargetResponse.model_validate(target) for target in mission.targets],
            complete_state=mission.complete_state
        )


