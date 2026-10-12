from fastapi import FastAPI
from db import Base, engine
from app import models  # noqa: F401  registra los modelos en Base.metadata
from app.routers import category, product

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventario Inteligente")
app.include_router(category.router)
app.include_router(product.router)
