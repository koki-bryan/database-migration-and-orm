from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Subject(Base):
    __tablename__= "subjects"
    
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column()