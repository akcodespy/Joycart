from fastapi import APIRouter, Depends,Request,Form,HTTPException,status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.db import get_db
from app.models import Seller
from app.auth import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/seller/check")
def seller_check(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    existing_seller = (
        db.query(Seller)
        .filter(Seller.user_id == current_user.id)
        .first()
    )

    if existing_seller:
        return RedirectResponse("/seller/dashboard", status_code=302)

    return RedirectResponse("/seller/registerform", status_code=302)
    
@router.post("/seller/register")
def register_seller(request: Request,store_name: str = Form(...),db: Session = Depends(get_db)):
        
    current_user = request.state.user
    seller = Seller(
    user_id=current_user.id,
    store_name=store_name
    )

    db.add(seller)
    db.commit()
    db.refresh(seller)

    return RedirectResponse("/seller/dashboard", status_code=302)

@router.get("/seller/dashboard")
def seller_dashboard(request: Request):
    return templates.TemplateResponse(
        "seller_dashboard.html",
        {"request": request}
    )

@router.get("/seller/registerform")
def seller_register_page(request: Request):
    return templates.TemplateResponse(
        "seller_register.html",
        {"request": request}
    )