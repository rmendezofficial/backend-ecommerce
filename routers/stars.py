from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Stars
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
import secrets
from fastapi.responses import JSONResponse
from .users import current_user

router=APIRouter(prefix='/stars',responses={404:{'message':'No encontrado'}})


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class starBase(BaseModel):
    product_id:int
    user_id:int
    order_id:int
    stars_number:int
  
@router.post('/create_star',status_code=status.HTTP_201_CREATED)
async def create_star(request:Request,star:starBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user_db=db.query(Users).filter(Users.id==star.user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db_existent=db.query(Stars).filter(Stars.user_id==star.user_id,Stars.product_id==star.product_id).first()
        if db_existent!=None:
            db_existent.stars_number=star.stars_number
            db.commit()
            return{'message':'Star successfuly updated'}
        db_star=Stars(**star.model_dump())
        db.add(db_star)
        db.commit()
        return{'message':'Star successfuly created'}
    return {'message':'CSRF FAILED'}

@router.delete('/delete_star/')
async def delete_user(request:Request,product_id:int,user_id:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user_db=db.query(Users).filter(Users.id==user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        star_db=db.query(Stars).filter(Stars.user_id==user_id,Stars.product_id==product_id).first()
        db.delete(star_db)
        db.commit()
        return {'message':'Star succesfuly deleted'}
    return {'message':'CSRF FAILED'}

