from pydantic import BaseModel, Field, ConfigDict

class CategoryBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=3, max_length=100)


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
