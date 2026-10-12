from fastapi import APIRouter, HTTPException, status

from dependencies import db_dependency
from app.schema.product import ProductCreate, ProductOut, ProductUpdate
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def get_or_404(service: ProductService, product_id: int):
    product = service.get_by_id(product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


@router.get("/", response_model=list[ProductOut])
def list_products(db: db_dependency):
    return ProductService(db).get_all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: db_dependency):
    return get_or_404(ProductService(db), product_id)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: db_dependency):
    return ProductService(db).create(data)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: db_dependency):
    service = ProductService(db)
    return service.update(get_or_404(service, product_id), data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: db_dependency):
    service = ProductService(db)
    service.delete(get_or_404(service, product_id))
