from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Comments
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
import secrets
from fastapi.responses import JSONResponse
from users import current_user

router=APIRouter(prefix='/comments',responses={404:{'message':'No encontrado'}})


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class CommentBase(BaseModel):
    user_id:int
    product_id:int
    comment:str
    
@router.post('/create_comment',status_code=status.HTTP_201_CREATED)
async def create_comment(request:Request,comment:CommentBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user=db.query(Users).filter(Users.id==comment.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db_comment=Comments(**comment.model_dump())
        db.add(db_comment)
        db.commit()
        return{'message':'Comment successfuly created'}
    return {'message':'CSRF FAILED'}

@router.put('/update_comment',status_code=status.HTTP_200_OK)
async def update_comment(request:Request,comment_id:int,comment:CommentBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user=db.query(Users).filter(Users.id==comment.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        comment_db=db.query(Comments).filter(Comments.id==comment_id).first()
        comment_db.comment=comment.comment
        comment_db.edited=True
        db.commit()
        return {'message':'Comment succesfuly updated'}
    return {'message':'CSRF FAILED'}

@router.delete('/delete_user/{comment_id}')
async def delete_comment(request:Request,comment_id:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    comment_db=db.query(Comments).filter(Comments.id==comment_id).first()
    user=db.query(Users).filter(Users.id==comment_db.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(comment_db)
        db.commit()
        return {'message':'Comment succesfuly deleted'}
    return {'message':'CSRF FAILED'}


