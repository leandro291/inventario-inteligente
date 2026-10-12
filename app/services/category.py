from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schema.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Category]:
        stmt = select(Category)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def create(self, data: CategoryCreate) -> Category:
        category = Category(**data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category, data: CategoryUpdate) -> Category:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()
