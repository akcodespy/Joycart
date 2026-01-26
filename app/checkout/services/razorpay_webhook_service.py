import json
from sqlalchemy.orm import Session
from app.checkout.services.checkout_services import place_order
from app.db.models import Checkout,User,Order,Refund

def handle_razorpay_event(
    db: Session,
    body: bytes
):
    payload = json.loads(body)
    event = payload.get("event")

    if event == "payment.captured":
        return handle_payment_captured(db, payload)

    if event in ("refund.processed", "refund.failed"):
        return handle_refund_event(db, payload, event)

    return {"status": "ignored"}

def handle_payment_captured(
    db,
    payload
):
    payment = payload["payload"]["payment"]["entity"]

    razorpay_order_id = payment["order_id"]
    razorpay_payment_id = payment["id"]
    method = payment["method"]

    checkout = db.query(Checkout).filter(
        Checkout.gateway_order_id == razorpay_order_id
    ).first()

    if not checkout:
        return {"status": "ignored"}

    existing_order = db.query(Order).filter(
        Order.checkout_id == checkout.checkout_id
    ).first()

    if existing_order:
        return {"status": "already_processed"}

    user = db.query(User).filter(
        User.id == checkout.user_id
    ).first()

    if not user:
        return {"status": "ignored"}

    place_order(
        current_user=user,
        db=db,
        checkout_id=checkout.checkout_id,
        method=method,
        gateway_payment_id=razorpay_payment_id
    )

    return {"status": "payment_processed"}


def handle_refund_event(
    db,
    payload,
    event: str
):
    refund_entity = payload["payload"]["refund"]["entity"]
    razorpay_refund_id = refund_entity["id"]

    refund = db.query(Refund).filter(
        Refund.gateway_refund_id == razorpay_refund_id
    ).first()

    if not refund:
        return {"status": "refund_not_found"}

    refund.status = (
        "REFUNDED" if event == "refund.processed" else "FAILED"
    )

    db.commit()

    return {"status": "refund_updated"}
