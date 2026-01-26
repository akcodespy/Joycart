from fastapi import APIRouter, Depends,Request
from sqlalchemy.orm import Session
from app.db.db import get_db
from fastapi.templating import Jinja2Templates
from app.db.models import User
from app.auth import get_current_user
from app.orders.services.orders_service import single_order,single_order_item,all_order_items,cancel_item

router = APIRouter()
pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/{order_id}")
def get_single_order(request: Request,
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    
):
    return single_order(order_id,current_user,db)


@router.get("/item/{item_id}")
def get_single_order_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return single_order_item(item_id,current_user,db)

@pages_router.get("/orders")
def get_all_order_items(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order_items = all_order_items(current_user,db)

    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request,
            "order_items": order_items,
            "current_user": current_user
        }
    )

@pages_router.get("/orders/{order_id}/{item_id}")
def order_detail_page(request: Request,
    current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "orderdetails.html",
        {"request": request,
         "current_user":current_user}
    )

@router.post("/item/{item_id}/cancel")
def cancel_order_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return cancel_item(item_id,current_user,db)



