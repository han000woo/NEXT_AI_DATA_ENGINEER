from fastapi import FastAPI
from routers import products,orders, users
from database import Base, engine

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping Mall API")

# 라우터 등록 (이게 핵심입니다)
app.include_router(products.router)
app.include_router(orders.router)