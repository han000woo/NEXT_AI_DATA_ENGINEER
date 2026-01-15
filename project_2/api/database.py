import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Docker 환경변수에서 가져오거나, 로컬 테스트용 기본값 사용
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()