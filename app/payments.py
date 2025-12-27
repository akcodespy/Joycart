from fastapi import APIRouter,Request
from fastapi import Depends
from app.db import get_db
from fastapi.templating import Jinja2Templates




router = APIRouter()

pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")


@pages_router.get("/payment/success")
def payment_success(request:Request):

    return templates.TemplateResponse(
        "prepaid_success.html",
        {
            "request": request
            }
    )
