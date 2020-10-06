from fastapi import FastAPI
from schemas import Item

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/items")
async def create_item(item: Item):
    """
    add a product
    """
    return item

