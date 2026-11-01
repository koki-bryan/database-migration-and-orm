from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Professor(Base):
    __tablename__ = "professors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
