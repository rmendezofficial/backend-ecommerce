from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Orders
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
import secrets
from fastapi.responses import JSONResponse
from .users import current_user

router=APIRouter(prefix='/orders',responses={404:{'message':'No encontrado'}})


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class orderBase(BaseModel):
    product_id:int
    user_id:int
    units:int
  
@router.post('/create_order',status_code=status.HTTP_201_CREATED)
async def create_order(request:Request,order:orderBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user_db=db.query(Users).filter(Users.id==order.user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db_order=Orders(**order.model_dump())
        db.add(db_order)
        db.commit()
        return{'message':'Order successfuly created'}
    return {'message':'CSRF FAILED'}

 
