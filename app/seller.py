from fastapi import APIRouter, Depends,Request,Form, File, UploadFile,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from app.db.db import get_db
from app.db.models import Seller,Product,OrderItems,Payment,Order
from fastapi import BackgroundTasks
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import json,os
from decimal import Decimal
from app.auth import get_current_seller,get_current_user
from app.orders import restore_stock_for_item,create_refund_record,initiate_razorpay_refund
from app.db.models import User


router = APIRouter()

pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)



####################Seller Register##################

@router.get("/seller/check")
def seller_check(request: Request,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    
    if current_user.is_seller:
        return RedirectResponse("/seller/dashboard", status_code=302)

    return RedirectResponse("/seller/registerform", status_code=302)
    
@router.post("/seller/register")
def register_seller(
    request: Request,
    background_tasks: BackgroundTasks,
    store_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    seller = Seller(
        user_id=current_user.id,
        store_name=store_name
    )
    current_user.is_seller = True

    db.add(seller)
    db.commit()
    db.refresh(seller)

    current_user.seller_id = seller.id

    if seller.id == 1 or seller.id == 2:
        
        background_tasks.add_task(populate_products, db, seller.id)

    return RedirectResponse("/seller/dashboard", status_code=302)

@pages_router.get("/seller/dashboard")
def seller_dashboard(request: Request,seller: Seller = Depends(get_current_seller)):
    return templates.TemplateResponse(
        "seller_dashboard.html",
        {"request": request
         }
    )

@pages_router.get("/seller/registerform")
def seller_register_page(request: Request):
    return templates.TemplateResponse(
        "seller_register.html",
        {"request": request}
    )



####################Product Create##################


@pages_router.get("/seller/product/add")
def seller_product_add(request: Request,seller: Seller = Depends(get_current_seller)):
    return templates.TemplateResponse(
        "seller_product_add.html",
        {"request": request}
    )

@router.post("/seller/product/create")
def create_product(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    sku: str = Form(...),
    price: Decimal = Form(...),
    discountPercentage: float = Form(0),
    stock: int = Form(...),
    availabilityStatus: str = Form(...),
    returnPolicy: str = Form(""),
    weight: int = Form(None),
    length: float = Form(None),
    width: float = Form(None),
    height: float = Form(None),
    shippingInformation: str = Form(""),
    warrantyInformation: str = Form(""),

    
    thumbnail: UploadFile = File(...),
    images: list[UploadFile] = File(...),

    db: Session = Depends(get_db),seller: Seller = Depends(get_current_seller)
):
    existing = db.query(Product).filter(
        Product.sku == sku,
        Product.seller_id == seller.id
    ).first()

    if existing:
        raise HTTPException(400, "SKU already exists")
    
    uploaded_public_ids = []
    try:
        thumb_result = cloudinary.uploader.upload(
            thumbnail.file,
            folder=f"products/{seller.id}/thumbnail"
        )
        
        public_id = thumb_result["public_id"]
        thumbnail_url, _  = cloudinary_url(
        public_id,
        width=300,
        height=300,
        crop="fill",
        gravity="auto",
        fetch_format="auto",
        quality="auto"
    )
        uploaded_public_ids.append(public_id)
        
            
        image_urls = [] 

        for img in images:
            result = cloudinary.uploader.upload(
                img.file,
                folder=f"products/{seller.id}/images"
            )
            public_id = result["public_id"]
            url, _ = cloudinary_url(
        public_id,
        width=1000,
        height=1000,
        crop="fill",
        gravity="auto",
        fetch_format="auto",
        quality="auto"
    )
            uploaded_public_ids.append(public_id)
            image_urls.append(url)

    
        if any(v is not None for v in (length, width, height)):
            dimensions = {
                "length": length,
                "width": width,
                "height": height
            }
        else:
            dimensions = None
    
        product = Product(
            seller_id=seller.id,
            title=title,
            description=description,
            category=category,
            sku=sku,
            price=price,
            discountPercentage=discountPercentage,
            stock=stock,
            availabilityStatus=availabilityStatus,
            returnPolicy=returnPolicy,
            weight=weight,
            dimensions=dimensions,
            shippingInformation=shippingInformation,
            warrantyInformation=warrantyInformation,
            thumbnail=thumbnail_url,
            images=image_urls,
        )

        db.add(product)
        db.commit()

    except Exception:
        db.rollback()
        for pid in uploaded_public_ids:
            cloudinary.uploader.destroy(pid)
        raise


    return RedirectResponse("/seller/dashboard", status_code=302)

@pages_router.get("/seller/products/edit/{product_id}")
def edit_product_page(
    request: Request,
    product_id: int,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == current_seller.id
    ).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")


    return templates.TemplateResponse(
        "seller_product_edit.html",{
            "request":request,
            "product":product}
    )





@router.post("/seller/products/editfn/{product_id}")
def edit_product(
    product_id: int,

    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    sku: str = Form(...),
    price: Decimal = Form(...),
    discountPercentage: float = Form(0),
    stock: int = Form(...),
    availabilityStatus: str = Form(...),
    returnPolicy: str = Form(""),

    weight: int = Form(None),
    length: float = Form(None),
    width: float = Form(None),
    height: float = Form(None),

    shippingInformation: str = Form(""),
    warrantyInformation: str = Form(""),

    thumbnail: UploadFile = File(None),
    images: list[UploadFile] = File([]),

    db: Session = Depends(get_db),
    seller: Seller = Depends(get_current_seller)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == seller.id
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    uploaded_public_ids = []

    try:
        
        if thumbnail and thumbnail.filename:
            result = cloudinary.uploader.upload(
                thumbnail.file,
                folder=f"products/{seller.id}/thumbnail"
            )

            public_id = result["public_id"]
            uploaded_public_ids.append(public_id)

            thumbnail_url, _ = cloudinary_url(
                public_id,
                width=300,
                height=300,
                crop="fill",
                gravity="auto",
                fetch_format="auto",
                quality="auto"
            )

            product.thumbnail = thumbnail_url  

       
        if images:
            new_image_urls = []

            for img in images:
                if not img.filename:
                    continue

                result = cloudinary.uploader.upload(
                    img.file,
                    folder=f"products/{seller.id}/images"
                )

                public_id = result["public_id"]
                uploaded_public_ids.append(public_id)

                url, _ = cloudinary_url(
                    public_id,
                    width=1000,
                    height=1000,
                    crop="fill",
                    gravity="auto",
                    fetch_format="auto",
                    quality="auto"
                )

                new_image_urls.append(url)

            if new_image_urls:
                product.images = new_image_urls  

        
        if any(v is not None for v in (length, width, height)):
            product.dimensions = {
                "length": length,
                "width": width,
                "height": height
            }
        else:
            product.dimensions = None

        
        product.title = title
        product.description = description
        product.category = category
        product.sku = sku
        product.price = price
        product.discountPercentage = discountPercentage
        product.stock = stock
        product.availabilityStatus = availabilityStatus
        product.returnPolicy = returnPolicy
        product.weight = weight
        product.shippingInformation = shippingInformation
        product.warrantyInformation = warrantyInformation

        db.commit()

    except Exception:
        db.rollback()
        for pid in uploaded_public_ids:
            cloudinary.uploader.destroy(pid)
        raise

    return RedirectResponse("/seller/products", status_code=302)

    

@router.post("/seller/products/delete/{product_id}")
def delete_product(
    product_id: int,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.seller_id == current_seller.id,
                                       Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()

    return RedirectResponse("/seller/products", status_code=302)

def populate_products(db: Session, seller_id: int):

    if seller_id ==1:
        file = "products1.json"
    else:
        file = "products2.json"

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("products", []):
        product = Product(
            seller_id=seller_id,

            title=item.get("title"),
            description=item.get("description"),
            category=item.get("category"),
            price=item.get("price"),
            discountPercentage=item.get("discountPercentage"),
            rating=item.get("rating"),
            stock=item.get("stock"),
            brand=item.get("brand"),
            sku=item.get("sku"),
            dimensions=item.get("dimensions"),
            weight=item.get("weight"),
            warrantyInformation=item.get("warrantyInformation"),
            availabilityStatus=item.get("availabilityStatus"),
            shippingInformation=item.get("shippingInformation"),
            returnPolicy=item.get("returnPolicy"),
            thumbnail=item.get("thumbnail"),
            images=item.get("images"),
        )

        db.add(product)

    db.commit()

#######seller product page############

@pages_router.get("/seller/products")
def seller_products(
    request: Request,
    db: Session = Depends(get_db),seller: Seller = Depends(get_current_seller)
):

    products = (
        db.query(Product)
        .filter(Product.seller_id == seller.id)
        .order_by(Product.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        "seller_products.html",
        {
            "request": request,
            "products": products
        }
    )

###############seller orders###############
@pages_router.get('/seller/orders')
def get_seller_order(request: Request,
    db: Session = Depends(get_db),seller: Seller = Depends(get_current_seller)):
    
    orderitems = (
    db.query(OrderItems, Product, Order)
    .join(Product, Product.id == OrderItems.product_id)
    .join(Order, Order.id == OrderItems.order_id)
    .filter(OrderItems.seller_id == seller.id)
    .order_by(OrderItems.id.desc())
    .all()
)
    order_ids = {order.id for _, _, order in orderitems}

    payments = (
    db.query(Payment)
    .filter(Payment.order_id.in_(order_ids))
    .order_by(Payment.created_at.desc())
    .all()
)
    payment_map = {}

    for payment in payments:
        if payment.order_id not in payment_map:
            payment_map[payment.order_id] = payment


    grouped_orders = {}

    for item, product, order in orderitems:

        if order.id not in grouped_orders:
            payment = payment_map.get(order.id)

            grouped_orders[order.id] = {
                "payment_status": payment.status,
                "items": []
            }

        grouped_orders[order.id]["items"].append({
            "item": item,
            "product": product
        })

    return templates.TemplateResponse(
    "seller_orders.html",
    {
        "request": request,
        "grouped_orders": grouped_orders
    }
)

@router.post("/seller/order-item/{item_id}/action")
def seller_order_item_action(
    item_id: int,
    action: str = Form(...),
    seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    refund = None 

    try:
        item = (
            db.query(OrderItems)
            .join(Order)
            .filter(
                OrderItems.id == item_id,
                OrderItems.seller_id == seller.id
            )
            .first()
        )

        if not item:
            raise HTTPException(404, "Order item not found")

        if item.status == "CANCELLED":
            return RedirectResponse("/seller/orders", status_code=302)

        valid_transitions = {
            "PLACED": ["CONFIRM", "CANCEL"],
            "CONFIRMED": ["SHIP", "CANCEL"],
            "SHIPPED": ["DELIVER"],
        }

        action = action.upper()

        if item.status not in valid_transitions:
            raise HTTPException(400, "Action not allowed")

        if action not in valid_transitions[item.status]:
            raise HTTPException(400, "Invalid action for this status")

        if action == "CONFIRM":
            item.status = "CONFIRMED"

        elif action == "SHIP":
            item.status = "SHIPPED"

        elif action == "DELIVER":
            item.status = "DELIVERED"

        elif action == "CANCEL":
            if item.status in ["SHIPPED", "DELIVERED"]:
                raise HTTPException(400, "Cannot cancel shipped item")

            restore_stock_for_item(item, db)
            item.status = "CANCELLED"
            refund = create_refund_record(item, db)

        db.commit()  

        if action == "CANCEL":
            initiate_razorpay_refund(refund, db)  

        return RedirectResponse("/seller/orders", status_code=302)

    except Exception as e:  
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database / gateway error: {str(e)}"
        )
