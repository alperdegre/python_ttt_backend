from sqlalchemy.orm import DeclerativeBase, relationship, sessionmaker

DATABASE_URL = "sqlite:///tictactoe.db"
engine = create_engine