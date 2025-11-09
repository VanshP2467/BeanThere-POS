from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
)

# SQLite file in the backend folder
DATABASE_URL = "postgresql+psycopg2://bean:coffee@localhost:5432/beanthere_pos"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
