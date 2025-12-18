from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float,Boolean
from app.db import Base
from sqlalchemy.orm import relationship
from typing import Optional
from datetime import datetime




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) 

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    store_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class OrderItems(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
                        
    
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # created | success | failed
    gateway = Column(String, nullable=False)
    gateway_payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    price = Column(Float)
    discount_percentage = Column(Float)
    rating = Column(Float)
    stock = Column(Integer)
    brand = Column(String)
    sku = Column(String)
    weight = Column(Integer)
    warranty = Column(String)
    shipping_info = Column(String)
    availability = Column(String)
    return_policy = Column(String)
    thumbnail = Column(String)
    images = Column(Text) 
    reviews = relationship("Review", back_populates="product")

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id')) # The Link
    rating = Column(Integer)
    comment = Column(String)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    reviewerName = Column(String)
    product = relationship("Product", back_populates="reviews")





