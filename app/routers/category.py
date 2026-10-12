from fastapi import APIRouter, HTTPException, status

from dependencies import db_dependency
from app.schema.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_or_404(service: CategoryService, category_id: int):
    category = service.get_by_id(category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return category


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: db_dependency):
    return CategoryService(db).get_all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: db_dependency):
    return get_or_404(CategoryService(db), category_id)


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: db_dependency):
    return CategoryService(db).create(data)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, data: CategoryUpdate, db: db_dependency):
    service = CategoryService(db)
    return service.update(get_or_404(service, category_id), data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: db_dependency):
    service = CategoryService(db)
    service.delete(get_or_404(service, category_id))
