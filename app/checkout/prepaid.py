from fastapi import APIRouter,Request,Form,Depends,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.models import Cart,Order,Payment,CartItem,Checkout,OrderItems,Product
import os,uuid,hmac,hashlib


pages_router = APIRouter()
router = APIRouter()

PAYMENT_WEBHOOK_SECRET = os.getenv("PAYMENT_WEBHOOK_SECRET")

if not PAYMENT_WEBHOOK_SECRET:
    raise RuntimeError("PAYMENT_WEBHOOK_SECRET is not set")


templates = Jinja2Templates(directory="templates")

@pages_router.get("/payment/start")
def prepaid_payment_page(
    request: Request,
    checkout_id: str,
    db: Session = Depends(get_db)
):
    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id
    ).first()

    if not checkout:
        raise HTTPException(404)

    return templates.TemplateResponse(
        "prepaid_confirm.html",
        {
            "request": request,
            "checkout_id": checkout_id,
            "amount": checkout.amount
        }
    )

@router.post("/checkout/prepaid/confirm")
def start_prepaid_payment(
    checkout_id: str = Form(...),
):
    return RedirectResponse(
        f"/prepaid-gateway?checkout_id={checkout_id}",
        status_code=302
    )

@pages_router.get("/prepaid-gateway")
def fake_gateway_page(
    request: Request,
    checkout_id: str
):
    
    gateway_payment_id = f"PAY-{uuid.uuid4().hex[:12]}"
    payload = f"{checkout_id}|SUCCESS|{gateway_payment_id}"
    signature = generate_signature(payload, PAYMENT_WEBHOOK_SECRET)

    return templates.TemplateResponse(
        "prepaid_gateway.html",
        {
            "request": request,
            "checkout_id": checkout_id,
            "signature": signature,
            "gateway_payment_id":gateway_payment_id
        }
    )

@router.post("/payment/webhook")
def payment_webhook(
    checkout_id: str = Form(...),
    payment_status: str = Form(...),
    signature: str = Form(...),
    gateway_payment_id: str = Form(...),
    db: Session = Depends(get_db)
):
    payload = f"{checkout_id}|{payment_status}|{gateway_payment_id}"


    expected_signature = generate_signature(
        payload,
        PAYMENT_WEBHOOK_SECRET
    )

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(403, "Invalid signature")
    
    if payment_status != "SUCCESS":
        raise HTTPException(400, "Payment failed")

    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id
    ).first()

    if not checkout:
        raise HTTPException(404)

    
    existing_order = db.query(Order).filter(
        Order.checkout_id == checkout.checkout_id
    ).first()

    if existing_order:
        return {"status": "already processed"}

    
    cart = db.query(Cart).filter(
        Cart.user_id == checkout.user_id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(400)

    
    product_ids = [item.product_id for item in cart.items]

    products = (
        db.query(Product)
        .filter(Product.id.in_(product_ids))
        .with_for_update()
        .all()
    )

    product_map = {p.id: p for p in products}

    total_amount = 0
    order_items = []

    for item in cart.items:
        product = product_map[item.product_id]

        if product.stock < item.quantity:
            raise HTTPException(400, "Out of stock")

        product.stock -= item.quantity
        total_amount += product.price * item.quantity

        order_items.append(
            OrderItems(
                product_id=product.id,
                quantity=item.quantity,
                seller_id=product.seller_id,
                price_at_purchase=product.price
            )
        )

    
    order = Order(
        user_id=checkout.user_id,
        checkout_id=checkout.checkout_id,
        amount=total_amount,
        shipping_address=checkout.shipping_address,
        status="PAID",
        currency="INR"
    )

    db.add(order)
    db.flush()

    for oi in order_items:
        oi.order_id = order.id

    payment = Payment(
        order_id=order.id,
        amount=order.amount,
        status="PAID",
        method="PREPAID",
        gateway_payment_id=gateway_payment_id
        
    )

    db.add_all(order_items)
    db.add(payment)

    
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.delete(checkout)
    db.commit()

    return RedirectResponse("/payment/success", status_code=302)

@pages_router.get("/payment/success")
def payment_success(request:Request):

    return templates.TemplateResponse(
        "prepaid_success.html",
        {
            "request": request
            }
    )


def generate_signature(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()