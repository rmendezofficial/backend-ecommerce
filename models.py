from sqlalchemy import Boolean,Column,Integer,String,DateTime,Text,Float
from database import Base
from sqlalchemy.sql import func


class Users(Base):
    __tablename__='users'
    
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(50),unique=True)
    password=Column(String(200))
    email=Column(String(100))
    disabled=Column(Boolean,default=False)
    token=Column(String(200),default=None)

class Products(Base):
    __tablename__='products'
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer)
    name=Column(String(50))
    description=Column(String(200))
    price=Column(Float)
    stock=Column(Integer)
    photo=Column(Text) 
    
class CartProducts(Base):
    __tablename__='cartproducts'
    
    id=Column(Integer,primary_key=True,index=True)
    product_id=Column(Integer)
    units=Column(Integer)
    user_id=Column(Integer)

class Comments(Base):
    __tablename__='comments'
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer)
    product_id=Column(Integer)
    comment=Column(String(200))
    edited=Column(Boolean,default=None)
    
class Orders(Base):
    __tablename__='orders'
    
    id=Column(Integer,primary_key=True,index=True)
    product_id=Column(Integer)
    user_id=Column(Integer)
    date=Column(DateTime, server_default=func.now())
    units=Column(Integer)

class Stars(Base):
    __tablename__='stars'
    
    id=Column(Integer,primary_key=True,index=True)
    product_id=Column(Integer)
    user_id=Column(Integer)
    order_id=Column(Integer)
    stars_number=Column(Integer)
