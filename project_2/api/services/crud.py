from sqlalchemy.orm import Session

from models import models
from schemas import schemas


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_order(db: Session, order: schemas.OrderCreate):
    # 상품 가격 조회
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        return None
    
    total_price = product.price * order.quantity
    db_order = models.Order(
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order