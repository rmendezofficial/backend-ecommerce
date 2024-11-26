from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,CartProducts,Products
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
import secrets
from fastapi.responses import JSONResponse
from .users import current_user

router=APIRouter(prefix='/cart',responses={404:{'message':'No encontrado'}})


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class CartBase(BaseModel):
    product_id:int
    user_id:int
    units:int

@router.post('/add_cart',status_code=status.HTTP_201_CREATED)
async def add_cart(request:Request,cart:CartBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    db_cart=CartProducts(**cart.model_dump())
    user=db.query(Users).filter(Users.id==cart.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.add(db_cart)
        db.commit()
        return{'message':'Cart successfuly created'}
    return {'message':'CSRF FAILED'}
  

@router.get('/get_cartproducts/',status_code=status.HTTP_200_OK)
async def get_cartproducts(request:Request,user_id:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    cartproducts_db=list(db.query(CartProducts).filter(CartProducts.user_id==user_id))
    products=[]
    for c in cartproducts_db:
        product_db=db.query(Products).filter(Products.id==c.product_id).first()
        product={
            'name':product_db.name,
            'product_id':c.product_id,
            'units':c.units,
            'cartproduct_id':c.id
        }
        products.append(product)
    user=db.query(Users).filter(Users.id==user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        return {'data':products}
    return {'message':'CSRF FAILED'} 
    
     

@router.delete('/delete_cart/}')
async def delete_cart(request:Request,cartproduct_id:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    cartproduct_db=db.query(CartProducts).filter(CartProducts.id==cartproduct_id).first()
    user=db.query(Users).filter(Users.id==cartproduct_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(cartproduct_db)
        db.commit()
        return {'message':'CartProduct succesfuly deleted'}
    return {'message':'CSRF FAILED'}

@router.put('/update_product')
async def update_product(request:Request,cartproduct_id:int,units:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    cartproduct_db=db.query(CartProducts).filter(CartProducts.id==cartproduct_id).first()
    user_db=db.query(Users).filter(Users.id==cartproduct_db.user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        cartproduct_db.units=units
        db.commit()
        return {'message':'CartProduct succesfuly updated'}
    return {'message':'CSRF FAILED'}
