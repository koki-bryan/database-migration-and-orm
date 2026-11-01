from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Assignment(Base):
    __tablename__= "assignments"
    
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    section: Mapped[str] = mapped_column()
    term: Mapped[int] = mapped_column()