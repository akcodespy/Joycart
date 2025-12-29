from fastapi import APIRouter,Request,Form ,Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.models import Cart,CartItem,Checkout,Payment,Order,OrderItems,Product
from app.db.db import get_db


templates = Jinja2Templates(directory="templates")

router = APIRouter()
pages_router = APIRouter()

@pages_router.get("/checkout/cod/confirm")
def cod_confirm_page(
    request: Request,
    checkout_id: str
):
    current_user = request.state.user
    return templates.TemplateResponse(
        "cod_confirm.html",
        {
            "request": request,
            "checkout_id": checkout_id
        }
    )

@router.post("/checkout/cod/confirm")
def place_cod_order(
    request: Request,
    checkout_id: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id,
        Checkout.user_id == current_user.id
    ).first()
    if not checkout:
        raise HTTPException(404)
    
    existing_order = db.query(Order).filter(
            Order.checkout_id == checkout.checkout_id
        ).first()

    if existing_order:
        return RedirectResponse(
            "/checkout/cod/orderplace",
            status_code=302
        )

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()
    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty")

    total_amount = 0
    order_items = []
    
    product_ids = [item.product_id for item in cart.items]
    products = (
        db.query(Product)
        .filter(Product.id.in_(product_ids))
        .with_for_update()
        .all()
    )
    product_map = {p.id: p for p in products}

    for item in cart.items:
        product = product_map.get(item.product_id)

        if not product:
            continue

        if product.stock < item.quantity:
            raise HTTPException(
                400, f"Insufficient stock for {product.title}"
            )

        subtotal = product.price * item.quantity
        total_amount += subtotal

        product.stock -= item.quantity

        order_items.append(
            OrderItems(
                product_id=product.id,
                quantity=item.quantity,
                seller_id=product.seller_id,
                price_at_purchase=product.price
            )
        )


    if total_amount == 0:
        raise HTTPException(400, "Invalid cart")

    order = Order(
        user_id=current_user.id,
        amount=total_amount,
        checkout_id=checkout.checkout_id,
        shipping_address=checkout.shipping_address,
        status="PLACED",
        currency="INR"
    )

    db.add(order)
    db.flush()   

    for oi in order_items:
        oi.order_id = order.id

    payment = Payment(
        order_id=order.id,
        amount=order.amount,
        status="DUE",
        method="COD"
    )

    db.add_all(order_items)
    db.add(payment)

    
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.delete(checkout)
    db.commit()

    return RedirectResponse(
        "/checkout/cod/orderplace",
        status_code=302
    )

@pages_router.get("/checkout/cod/orderplace")
def cod_order_success(request:Request):
    return templates.TemplateResponse(
        "cod_success.html",
        {"request":request}
    )