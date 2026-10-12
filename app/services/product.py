from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schema.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Product]:
        stmt = select(Product)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product, data: ProductUpdate) -> Product:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()