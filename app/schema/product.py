from pydantic import BaseModel, Field, ConfigDict

class ProductBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int = Field(gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=3, max_length=100)
    precio: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category_id: int | None = Field(None, gt=0)


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int