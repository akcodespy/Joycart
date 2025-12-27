from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.db import get_db
from app.models import Product

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/products/{product_id}")
def product_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return templates.TemplateResponse(
        "product.html",
        {
            "request": request,
            "product": product
        }
    )

def list_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.desc()).all()
    
@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "price": p.price
        }
        for p in products
    ]


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "title": product.title,
        "price": product.price,
        "description": product.description,
        "stock": product.stock
    }



