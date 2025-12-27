from fastapi import APIRouter, Depends, HTTPException, Request,Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Cart, CartItem, Product


router = APIRouter()
pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.post("/add")
def add_to_cart(request:Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db),
):
    current_user = request.state.user
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    
    item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        .first()
    )

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)

    db.commit()
    db.refresh(cart)

    return cart

@router.get("/view")
def get_cart(request: Request,
    db: Session = Depends(get_db),
    
):
    current_user = request.state.user
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        return {"items": [], "total": 0}

    items = []
    total = 0

    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue

        subtotal = product.price * item.quantity
        total += subtotal

        items.append({
            "id": item.id,
            "product_id": product.id,
            "title": product.title,
            "price": product.price,
            "quantity": item.quantity,
            "subtotal": subtotal,
            "thumbnail": product.thumbnail
        })

    return {
        "items": items,
        "total": total
    }


@router.patch("/item/{item_id}")
def update_quantity(request: Request,
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    
):
    current_user = request.state.user
    item = (db.query(CartItem).join(Cart).filter(CartItem.id == item_id,Cart.user_id == current_user.id).first())
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.quantity = quantity
    db.commit()

    return {"message": "Quantity updated"}



@router.delete("/item/{item_id}")
def delete_quantity(request: Request,
    item_id: int,
    db: Session = Depends(get_db),
    
):
    current_user = request.state.user
    item = (db.query(CartItem).join(Cart).filter(CartItem.id == item_id,Cart.user_id == current_user.id).first())
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

    return {"message": "Item removed"}

@pages_router.get("/cart")
def viewcart(request: Request):   
    return templates.TemplateResponse(
        "viewcart.html",
        {"request":request}
    )
