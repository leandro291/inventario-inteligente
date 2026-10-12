from fastapi import FastAPI
from app.routers import category, product

app = FastAPI(title="Inventario Inteligente")
app.include_router(category.router)
app.include_router(product.router)
