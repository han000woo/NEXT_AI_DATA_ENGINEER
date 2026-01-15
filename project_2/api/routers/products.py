from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import order, product
from database import get_db
from schemas import schemas
# 실제론 schemas, models를 임포트 해야 함 (여기선 약식으로 표현)

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product.get_products(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Product)
def create_product(product_item: schemas.ProductCreate, db: Session = Depends(get_db)):
    return product.create_product(db=db, product=product_item)

@router.put("/{product_id}")
def update_product(product_id : int, product_item: schemas.ProductUpdate, db: Session = Depends(get_db)) :
    updated_product = product.update_product(db, product_id, product_item)
    if update_product is None : 
        raise HTTPException(status_code = 404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}")
def delete_product(product_id : int, db:Session = Depends(get_db)) : 
    success = product.delete_product(db, product_id)
    if not success : 
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Deleted successfully"}