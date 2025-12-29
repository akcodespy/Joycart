from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.models import Cart,Product,Checkout,Address,CartItem
from datetime import datetime,timedelta
import uuid

router = APIRouter()
pages_router = APIRouter()

_last_cleanup = None #lazy cleanup 



templates = Jinja2Templates(directory="templates")

@router.post("/checkout/start")
def start_checkout(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    lazy_cleanup_checkouts(db)

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty")

    total_amount = 0
    for item in cart.items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()
        total_amount += product.price * item.quantity

    checkout = Checkout(
        checkout_id=str(uuid.uuid4()),
        user_id=current_user.id,
        amount=total_amount
    )

    db.add(checkout)
    db.commit()

    return {
        "redirect_url": f"/checkout/address?checkout_id={checkout.checkout_id}"
    }

@pages_router.get("/checkout/address")
def checkout_address_page(
    request: Request,
    checkout_id: str,
    db: Session = Depends(get_db)
):
    
    current_user = request.state.user

    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id,
        Checkout.user_id == current_user.id
    ).first()

    if not checkout:
        raise HTTPException(404)

    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).all()

    return templates.TemplateResponse(
        "checkout_delivery_address.html",
        {
            "request": request,
            "addresses": addresses,
            "checkout_id": checkout_id
        }
    )

@router.post("/checkout/address")
def save_checkout_address(
    request:Request,
    checkout_id: str = Form(...),
    selected_address_id: int = Form(...),
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id,
        Checkout.user_id == current_user.id
    ).first()

    if not checkout:
        raise HTTPException(404)

    address = db.query(Address).filter(
        Address.id == selected_address_id,
        Address.user_id == current_user.id
    ).first()

    checkout.shipping_address = {
        "name": address.name,
        "phone": address.phone,
        "address_line1": address.address_line1,
        "city": address.city,
        "state": address.state,
        "pincode": address.pincode
    }

    db.commit()

    return RedirectResponse(
        f"/checkout/summary?checkout_id={checkout_id}",
        status_code=302
    )

@pages_router.get("/checkout/summary")
def checkout_summary(
    request: Request,
    checkout_id: str,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    
    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id,
        Checkout.user_id == current_user.id
    ).first()

    if not checkout or not checkout.shipping_address:
        raise HTTPException(400)

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        raise HTTPException(400, "Cart not found")

    items = (
        db.query(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )


    return templates.TemplateResponse(
        "checkout_summary.html",
        {
            "request": request,
            "checkout": checkout,
            "items": items,
            "checkout_id": checkout_id
        }
    )

@router.post("/checkout/confirm")
def confirm_checkout(
    checkout_id: str = Form(...),
    db: Session = Depends(get_db)
):
    
    return RedirectResponse(
        f"/checkout/payment?checkout_id={checkout_id}",
        status_code=302
    )


@pages_router.get("/checkout/payment")
def checkout_payment_page(
    request: Request,
    checkout_id: str,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id,
        Checkout.user_id == current_user.id
    ).first()

    if not checkout or not checkout.shipping_address:
        raise HTTPException(400, "Invalid checkout")

    return templates.TemplateResponse(
        "checkout_payment.html",
        {
            "request": request,
            "checkout_id": checkout_id,
            "amount": checkout.amount
        }
    )

@router.post("/checkout/payment")
def select_payment_method(
    request:Request,
    checkout_id: str = Form(...),
    payment_method: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    checkout = db.query(Checkout).filter(
        Checkout.checkout_id == checkout_id,
        Checkout.user_id == current_user.id
    ).first()

    if not checkout:
        raise HTTPException(404)

    checkout.payment_method = payment_method
    db.commit()


    if payment_method == "COD":
        return RedirectResponse(
            f"/checkout/cod/confirm?checkout_id={checkout_id}",
            status_code=302
        )

    
    return RedirectResponse(
        f"/checkout/prepaid/confirm?checkout_id={checkout_id}",
        status_code=302
    )

def lazy_cleanup_checkouts(db):
    global _last_cleanup

    now = datetime.utcnow()

    if _last_cleanup and now - _last_cleanup < timedelta(minutes=10):
        return

    db.query(Checkout).filter(
        Checkout.expires_at < now
    ).delete()

    db.commit()
    _last_cleanup = now


