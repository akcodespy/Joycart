from fastapi import APIRouter, Depends,Request,Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.db import get_db
from app.models import Seller
from app.auth import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/seller/check", dependencies=[Depends(get_current_user)])
def seller_check(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    existing_seller = (
        db.query(Seller)
        .filter(Seller.user_id == current_user.id)
        .first()
    )

    if existing_seller:
        return RedirectResponse("/seller/dashboard", status_code=302)

    return RedirectResponse("/seller/register", status_code=302)


@router.get("/seller/dashboard", dependencies=[Depends(get_current_user)])
def seller_dashboard(request: Request):
    return templates.TemplateResponse(
        "seller_dashboard.html",
        {"request": request}
    )

@router.get("/seller/register", dependencies=[Depends(get_current_user)])
def seller_register_page(request: Request):
    return templates.TemplateResponse(
        "seller_register.html",
        {"request": request}
    )