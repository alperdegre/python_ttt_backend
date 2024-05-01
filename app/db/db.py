from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
 
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__= "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()

DATABASE_URL = "sqlite:///tictactoe.db"
engine = create_engine(
    DATABASE_URL,
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()