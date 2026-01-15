from sqlalchemy.orm import Session

from models import product, order
from schemas import schemas


def create_order(db: Session, order_item: schemas.OrderCreate):
    # 상품 가격 조회
    product = db.query(product.Product).filter(product.Product.id == order_item.product_id).first()
    if not product:
        return None
    
    total_price = product.price * order_item.quantity
    db_order = order.Order(
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        total_price=total_price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def create_bulk_orders(db: Session, orders : list[schemas.OrderCreate]) :
    product_ids = [order_item.product_id for order_item in orders] 

    products_data = db.query(
        product.Product.id,
        product.Product.price
    ).filter(product.Product.id.in_(product_ids)).all()

    price_map = {p.id: p.price for p in products_data}

    db_orders = [] 
    for order_item in orders : 
        if order_item.product_id in price_map :
            current_price = price_map[order_item.product_id]
            total = current_price * order_item.quantity 

            new_order = order.Order(
                product_id = order_item.product_id,
                quantity = order_item.quantity, 
                total_price = total
            )
            db_orders.append(new_order)
        
    if db_orders:
        db.add_all(db_orders)
        db.commit() 
    
    return db_orders
    