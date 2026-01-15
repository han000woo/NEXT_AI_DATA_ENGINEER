from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import crud
from database import get_db
from schemas import schemas
# 실제론 schemas, models를 임포트 해야 함 (여기선 약식으로 표현)

router = APIRouter(prefix="/orders", tags=["users"])

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = crud.create_order(db=db, order=order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_order