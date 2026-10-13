from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine
from app import models 
from app.routers import ai, category, product

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventario Inteligente")

# ponytail: orígenes fijos de desarrollo; mover a .env cuando haya front desplegado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category.router)
app.include_router(product.router)
app.include_router(ai.router)
