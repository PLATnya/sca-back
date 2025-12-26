from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
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

