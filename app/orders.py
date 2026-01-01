from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from app.db.db import get_db
from fastapi.templating import Jinja2Templates
from app.db.models import Order, OrderItems, Product,Payment
import uuid


router = APIRouter()
pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/{order_id}")
def get_single_order(request: Request,
    order_id: int,
    db: Session = Depends(get_db),
    
):
    current_user = request.state.user
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = (
        db.query(OrderItems, Product)
        .join(Product, Product.id == OrderItems.product_id)
        .filter(OrderItems.order_id == order.id)
        .all()
    )
    data = {
        "id": order.id,
        "amount": order.amount,
        "currency": order.currency,
        "status": order.status,
        "created_at": order.created_at,
        "items": [
            {
                "product_id": product.id,
                "title": product.title,
                "price": oi.price_at_purchase,
                "quantity": oi.quantity,
                "subtotal": oi.price_at_purchase * oi.quantity
            }
            for oi, product in items
        ],
        "payment": None
    }

    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .order_by(Payment.created_at.desc())
        .first()
    )

    if payment:
        data["payment"] = {
            "method": payment.method,
            "status": payment.status,
            "gateway_id": payment.gateway_payment_id
        }

    return data

@pages_router.get("/orders")
def get_all_orders(request: Request, db: Session = Depends(get_db)):

    current_user = request.state.user 
    
    orders = db.query(Order).filter(Order.user_id ==current_user.id).order_by(Order.created_at.desc()).all()

    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request, 
            "orders": orders
            
        }
    )

#######################################CANCEL AND REFUND ORDERS###################################

@router.post("/cancel/{order_id}")
def cancel_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status in ["CANCELLED", "REFUNDED"]:
        raise HTTPException(400, "Order already cancelled")

    
    order_items = db.query(OrderItems).filter(
        OrderItems.order_id == order.id
    ).all()

    if not order_items:
        raise HTTPException(400, "No order items found")

    
    for item in order_items:
        if item.status in ["SHIPPED", "DELIVERED"]:
            raise HTTPException(
                400,
                "Order cannot be cancelled. Some items already shipped."
            )

    refund_amount = 0

    
    for item in order_items:
        if item.status == "PLACED":
            item.status = "CANCELLED"

            
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()
            if product:
                product.stock += item.quantity

            refund_amount += item.price_at_purchase * item.quantity

    
    order.status = "CANCELLED"

   
    if refund_amount > 0:
        payment = Payment(
            order_id=order.id,
            amount=refund_amount,
            status="REFUNDED",
            method="SYSTEM ",
            gateway_payment_id=f"REFUND-{uuid.uuid4().hex[:12]}"
        )
        db.add(payment)

    db.commit()

    return {
        "message": "Order cancelled successfully",
        "order_id": order.id
    }

@pages_router.get("/orders/{order_id}")
def order_detail_page(request: Request):
    return templates.TemplateResponse(
        "orderdetails.html",
        {"request": request}
    )

