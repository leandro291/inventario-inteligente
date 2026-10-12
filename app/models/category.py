from db import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class Category(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)