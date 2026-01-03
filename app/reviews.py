from fastapi import APIRouter,Form,Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user
from app.db.models import User,Review,OrderItems,Order
from app.db.db import get_db

router = APIRouter()
pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")



@router.post("/reviews/add")
def add_review(
    product_id: int = Form(...),
    rating: int = Form(...),
    comment: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if rating < 1 or rating > 5:
        raise HTTPException(400, "Rating must be between 1 and 5")

    
    has_bought = db.query(OrderItems).join(
        Order, Order.id == OrderItems.order_id
    ).filter(
        Order.user_id == current_user.id, 
        OrderItems.product_id == product_id,
        OrderItems.status == "DELIVERED"
    ).first() is not None

    if not has_bought:
        raise HTTPException(
            403,
            "Only people who bought this product can add a review"
        )

    
    existing_review = db.query(Review).filter(
        Review.product_id == product_id,
        Review.user_id == current_user.id
    ).first()

    if existing_review:
        raise HTTPException(400, "You already reviewed this product")

    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )

    db.add(review)
    db.commit()

    return {"message": "Review added"}


@router.get("/reviews/load")
def load_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    reviews = (
        db.query(Review, User.username)
        .join(User, User.id == Review.user_id)
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return [
        {
            "username": username,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        }
        for review, username in reviews
    ]


@router.get("/reviews/calculate")
def calculate_rating(
    product_id: int,
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).all()

    if not reviews:
        return {
            "average_rating": 0,
            "total_reviews": 0
        }

    total_rating = sum(r.rating for r in reviews)
    average_rating = round(total_rating / len(reviews), 1)

    return {
        "average_rating": average_rating,
        "total_reviews": len(reviews)
    }