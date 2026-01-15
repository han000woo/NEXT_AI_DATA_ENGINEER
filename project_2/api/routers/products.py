from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services import crud
from database import get_db
from schemas import schemas
# 실제론 schemas, models를 임포트 해야 함 (여기선 약식으로 표현)

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)