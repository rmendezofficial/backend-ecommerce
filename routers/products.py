from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Products,Comments,Stars,Orders
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
import secrets
from fastapi.responses import JSONResponse
from .users import current_user
import random

router=APIRouter(prefix='/products',responses={404:{'message':'No encontrado'}})


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
     
class ProductBase(BaseModel):
    name:str
    description:str
    price:float
    stock:int
    user_id:int
    photo:str

@router.post('/create_product',status_code=status.HTTP_201_CREATED)
async def create_post(request:Request,product:ProductBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    db_product=Products(**product.model_dump())
    user=db.query(Users).filter(Users.id==product.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.add(db_product)
        db.commit()
        return{'message':'Product successfuly created'}
    return {'message':'CSRF FAILED'}
  

@router.get('/get_product/{product_id}',status_code=status.HTTP_200_OK)
async def get_post(product_id:int,db:Session=Depends(get_db)):
    product_db=db.query(Products).filter(Products.id==product_id).first()
    user=db.query(Users).filter(Users.id==product_db.user_id).first()
    comments=list(db.query(Comments).filter(Comments.product_id==product_db.id))
    stars=list(db.query(Stars).filter(Stars.product_id==product_db.id))
    stars_num=len(stars)
    orders=list(db.query(Orders).filter(Orders.product_id==product_id))
    orders_num=len(orders)
    
    avg_stars_sum=0
    users_stars_num=0
    for star in stars:
        avg_stars_sum+=star.stars_number
        users_stars_num+=1
    avg_final=avg_stars_sum/users_stars_num
    
    comments_final=[]
    for c in comments:
        user=db.query(Users).filter(Users.id==c.user_id).first()
        new_comment={'comment':c.comment,'id':c.id,'user_id':c.user_id,'username':user.username}
        comments_final.append(new_comment)
    prod_req={
        'id':product_db.id,
        'name':product_db.name,
        'description':product_db.description,
        'photo':product_db.photo,
        'user_id':product_db.user_id,
        'username':user.username,
        'comments':comments_final,
        'comments_num':len(comments),
        'stars':stars_num,
        'stars_db':stars,
        'stars_avg':avg_final,
        'price':product_db.price,
        'stock':product_db.stock,
        'orders_num':orders_num
    }
    return prod_req

@router.get('/get_products/',status_code=status.HTTP_200_OK)
async def get_products(db:Session=Depends(get_db)):
    products=list(db.query(Products))
    if products:
        random.shuffle(products)
        products_final=[]
        for p in products:
            user=db.query(Users).filter(Users.id==p.user_id).first()
            
            stars=list(db.query(Stars).filter(Stars.product_id==p.id))
            stars_num=len(stars)
            orders=list(db.query(Orders).filter(Orders.product_id==p.id))
            orders_num=len(orders)
            
            avg_stars_sum=0
            users_stars_num=0
            for star in stars:
                avg_stars_sum+=star.stars_number
                users_stars_num+=1
            avg_final=avg_stars_sum/users_stars_num
                    
            new_product={
                'id':p.id,
                'name': p.name,
                'description': p.description,
                'photo': p.photo,
                'username': user.username,
                'user_id': user.id,
                'id': p.id,
                'price':p.price,
                'stock':p.stock,
                'stars':stars_num,
                'stars_db':stars,
                'stars_avg':avg_final,
                'orders_num':orders_num
            }
            products_final.append(new_product)
            
        return products_final
    return {'message':'No posts'}

@router.delete('/delete_product/}')
async def delete_product(request:Request,product_id:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    product_db=db.query(Products).filter(Products.id==product_id).first()
    user=db.query(Users).filter(Users.id==product_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(product_db)
        db.commit()
        return {'message':'Product succesfuly deleted'}
    return {'message':'CSRF FAILED'}

@router.put('/update_product')
async def update_product(request:Request,product_id:int,stock:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    product_db=db.query(Products).filter(Products.id==product_id).first()
    user_db=db.query(Users).filter(Users.id==product_db.user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        product_db.stock=stock
        db.commit()
        return {'message':'Product succesfuly updated'}
    return {'message':'CSRF FAILED'}

@router.get('/search')
async def search(query:str,db:Session=Depends(get_db)):
    results=list(db.query(Products).filter(Products.name.ilike(f"%{query}%")))
    return results
