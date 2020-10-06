from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/products")
async def products():
    """
    add a product
    """
    return {"message": "product added"}

