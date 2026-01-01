from fastapi import APIRouter,Request,Form,Depends,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.db import get_db
import os,uuid,hmac,hashlib
from app.db.models import Checkout
from app.checkout.helper import helper



pages_router = APIRouter()
router = APIRouter()

PAYMENT_WEBHOOK_SECRET = os.getenv("PAYMENT_WEBHOOK_SECRET")

if not PAYMENT_WEBHOOK_SECRET:
    raise RuntimeError("PAYMENT_WEBHOOK_SECRET is not set")


templates = Jinja2Templates(directory="templates")

@pages_router.get("/checkout/prepaid/confirm")
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
        f"/checkout/prepaid/gateway?checkout_id={checkout_id}",
        status_code=302
    )

@pages_router.get("/checkout/prepaid/gateway")
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

@router.post("/checkout/prepaid/webhook")
def payment_webhook(request:Request,
    checkout_id: str = Form(...),
    payment_status: str = Form(...),
    signature: str = Form(...),
    gateway_payment_id: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    payload = f"{checkout_id}|{payment_status}|{gateway_payment_id}"

    expected_signature = generate_signature(
        payload,
        PAYMENT_WEBHOOK_SECRET
    )

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(403, "Invalid signature")
    
    if payment_status != "SUCCESS":
        raise HTTPException(400, "Payment failed")
    
    method = "PREPAID"

    helper(current_user,db,checkout_id,method,gateway_payment_id)

    return RedirectResponse("/checkout/prepaid/success", status_code=302)

@pages_router.get("/checkout/prepaid/success")
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