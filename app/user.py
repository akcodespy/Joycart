# app/crud/user.py
from fastapi import APIRouter, Depends, HTTPException,Form,Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import get_db
from fastapi.templating import Jinja2Templates
from app.auth import hash_password, verify_password, create_access_token,get_current_user
from app.models import User, Address
from app.schemas import UserOut
from app.product import list_products


router = APIRouter()
pages_router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.post("/register")
def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="username already exists")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="email already exists")

    user = User(
        username=username,
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/login", status_code=302)

@pages_router.get("/register")
def register(request: Request):
     
    token = request.cookies.get("access_token")

    if token:
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@router.post("/login")
def login_user( username: str = Form(...),
    password: str = Form(...), 
    db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(password, user.password):
        return RedirectResponse(
            "/login?error=1",
            status_code=302
        )

    token = create_access_token({"sub": user.username})

    response = RedirectResponse(
        "/dashboard",
        status_code=302
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24,
        samesite="lax",
        secure=False,
        path="/"  
    )

    return response

@pages_router.get('/login')
def login(request: Request):
    token = request.cookies.get("access_token")

    if token:
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@router.post("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response

@pages_router.get("/dashboard", dependencies=[Depends(get_current_user)])
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    products = list_products(db)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "products": products}
    )


@pages_router.get("/profile")
def profile(
    request: Request,
    current_user = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "username": current_user.username,
            "email": current_user.email
        }
    )


@router.post("/address/add")
def add_address(current_user: User = Depends(get_current_user),
    name: str = Form(...),
    phone: str = Form(...),
    address_line1: str = Form(...),
    address_line2: str = Form(None),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    is_default: bool = Form(False),
    db: Session = Depends(get_db)
):

    if is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})

    address = Address(
        user_id=current_user.id,
        name=name,
        phone=phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        pincode=pincode,
        is_default=is_default
    )

    db.add(address)
    db.commit()

    return RedirectResponse("/profile", status_code=302)

@pages_router.get('/address/form', dependencies=[Depends(get_current_user)])
def add_address(request: Request):
    return templates.TemplateResponse(
        "address_form.html",
        {"request":request}
        )

@pages_router.get("/addresses")
def get_address(request:Request,current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):

    addresses = db.query(Address).filter(Address.user_id ==current_user.id).all()

    return templates.TemplateResponse(
        "address.html",{
            'request':request,
            'addresses':addresses
        }
    )