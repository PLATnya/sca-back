from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import models
import schemas
from database import get_db, engine
from breed_validator import validate_breed, get_breed_names

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SCA Backend API"
)


@app.get("/")
def read_root():
    return {"message": "HI"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/cats/", response_model=schemas.CatResponse, status_code=status.HTTP_201_CREATED)
def create_cat(cat: schemas.CatCreate, db: Session = Depends(get_db)):
    """Create a new cat. Breed must be validated against the Cat API."""
    # Validate breed against Cat API
    if not validate_breed(cat.breed):
        valid_breeds = get_breed_names()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Invalid breed: '{cat.breed}'. Breed must be one of the valid breeds from the Cat API.",
                "valid_breeds": valid_breeds[:20] if len(valid_breeds) > 20 else valid_breeds  
            }
        )
    
    db_cat = models.Cat(**cat.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@app.get("/cats/", response_model=List[schemas.CatResponse])
def list_cats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all cats with pagination"""
    cats = db.query(models.Cat).offset(skip).limit(limit).all()
    return cats


@app.get("/cats/{cat_id}", response_model=schemas.CatResponse)
def get_cat(cat_id: int, db: Session = Depends(get_db)):
    """Get a single cat by ID"""
    cat = db.query(models.Cat).filter(models.Cat.id == cat_id).first()
    if cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cat with id {cat_id} not found"
        )
    return cat


@app.put("/cats/{cat_id}", response_model=schemas.CatResponse)
def update_cat(cat_id: int, cat: schemas.CatUpdate, db: Session = Depends(get_db)):
    """Update cat's salary (only salary can be updated)"""
    db_cat = db.query(models.Cat).filter(models.Cat.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cat with id {cat_id} not found"
        )
    
    # Update only salary
    db_cat.salary = cat.salary
    
    db.commit()
    db.refresh(db_cat)
    return db_cat


@app.delete("/cats/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cat(cat_id: int, db: Session = Depends(get_db)):
    """Remove a cat"""
    db_cat = db.query(models.Cat).filter(models.Cat.id == cat_id).first()
    if db_cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cat with id {cat_id} not found"
        )
    
    db.delete(db_cat)
    db.commit()
    return None


# Mission CRUD endpoints

@app.post("/missions/", response_model=schemas.MissionResponse, status_code=status.HTTP_201_CREATED)
def create_mission(mission: schemas.MissionCreate, db: Session = Depends(get_db)):
    """Create a new mission with targets. Each target is unique to the mission."""
    # Create mission without cat assignment
    db_mission = models.Mission(
        cat_id=None,
        complete_state=False
    )
    db.add(db_mission)
    db.flush()  # Flush to get the mission ID
    
    # Create targets for this mission
    for target_data in mission.targets:
        db_target = models.Target(
            mission_id=db_mission.id,
            name=target_data.name,
            country=target_data.country,
            notes=target_data.notes,
            complete_state=False
        )
        db.add(db_target)
    
    db.commit()
    db.refresh(db_mission)
    return schemas.MissionResponse.from_orm(db_mission)


@app.get("/missions/", response_model=List[schemas.MissionResponse])
def list_missions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all missions with pagination"""
    missions = db.query(models.Mission).offset(skip).limit(limit).all()
    return [schemas.MissionResponse.from_orm(mission) for mission in missions]


@app.get("/missions/{mission_id}", response_model=schemas.MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    """Get a single mission by ID"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    return schemas.MissionResponse.from_orm(mission)


@app.post("/missions/{mission_id}/assign-cat", response_model=schemas.MissionResponse)
def assign_cat_to_mission(mission_id: int, assignment: schemas.MissionAssignCat, db: Session = Depends(get_db)):
    """Assign a cat to a mission"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    # Check if mission already has a cat assigned
    if mission.cat_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mission with id {mission_id} is already assigned to cat {mission.cat_id}"
        )
    
    # Validate cat exists
    cat = db.query(models.Cat).filter(models.Cat.id == assignment.cat_id).first()
    if cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cat with id {assignment.cat_id} not found"
        )
    
    mission.cat_id = assignment.cat_id
    db.commit()
    db.refresh(mission)
    return schemas.MissionResponse.from_orm(mission)


@app.put("/missions/{mission_id}/targets", response_model=schemas.MissionResponse)
def update_mission_targets(mission_id: int, update: schemas.MissionUpdateTargets, db: Session = Depends(get_db)):
    """Update mission targets"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    # Check if mission is completed
    if mission.complete_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update targets: Mission is already completed"
        )
    
    # Delete existing targets
    existing_targets = db.query(models.Target).filter(models.Target.mission_id == mission_id).all()
    for target in existing_targets:
        db.delete(target)
    
    # Create new targets
    for target_data in update.targets:
        db_target = models.Target(
            mission_id=mission.id,
            name=target_data.name,
            country=target_data.country,
            notes=target_data.notes,
            complete_state=False
        )
        db.add(db_target)
    
    db.commit()
    db.refresh(mission)
    return schemas.MissionResponse.from_orm(mission)


@app.put("/missions/{mission_id}/complete", response_model=schemas.MissionResponse)
def mark_mission_complete(mission_id: int, db: Session = Depends(get_db)):
    """Mark a mission as completed"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    if mission.complete_state:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mission is already completed"
        )
    
    mission.complete_state = True
    db.commit()
    db.refresh(mission)
    return schemas.MissionResponse.from_orm(mission)


@app.put("/missions/{mission_id}/targets/{target_id}/notes", response_model=schemas.MissionResponse)
def update_target_notes(mission_id: int, target_id: int, update: schemas.MissionUpdateNotes, db: Session = Depends(get_db)):
    """Update notes for a target. Notes cannot be updated if target or mission is completed."""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    if mission.complete_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update notes: Mission is already completed"
        )
    
    target = db.query(models.Target).filter(
        models.Target.id == target_id,
        models.Target.mission_id == mission_id
    ).first()
    
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with id {target_id} not found in mission {mission_id}"
        )
    
    if target.complete_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update notes: Target is already completed"
        )
    
    target.notes = update.notes
    db.commit()
    db.refresh(mission)
    return schemas.MissionResponse.from_orm(mission)


@app.delete("/missions/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_mission(mission_id: int, db: Session = Depends(get_db)):
    """Remove a mission. A mission cannot be deleted if it is already assigned to a cat."""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    if mission.cat_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete mission: Mission is assigned to a cat"
        )
    
    db.delete(mission)
    db.commit()
    return None



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)