# public modules
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

# from this project

from . import models, schemas
from app.models import *
from app.schemas import *

from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/items")
async def create_item(item: ItemSchema, db: Session = Depends(get_db)):
    """
    add a product
    """
    if item.price == 99.99:
        raise HTTPException(
            status_code=404, detail="Are errors really this easy with fastapi?!"
        )

    new_item = ItemModel(name=item.name, description=item.description, price=item.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return item


@app.get("/items", response_model=List[ItemSchema])
async def get_items(db: Session = Depends(get_db)):
    """
    get all items
    """
    return db.query(ItemModel).all()

