from sqlalchemy.orm import Session

from models import product
from schemas import schemas


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(product.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = product.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_data: schemas.ProductUpdate):
    db_product = db.query(product.Product).filter(product.Product.id == product_id).first()
    if db_product:
        # 데이터 갱신
        db_product.name = product_data.name
        db_product.description = product_data.description
        db_product.price = product_data.price
        db_product.image_url = product_data.image_url
        db_product.category = product_data.category
        
        db.commit()
        db.refresh(db_product)
        return db_product
    return None

def delete_product(db: Session, product_id: int):
    db_product = db.query(product.Product).filter(product.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False