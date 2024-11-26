from fastapi import FastAPI
from database import engine,SessionLocal,Base
from fastapi.middleware.cors import CORSMiddleware
from routers import users,cart,comments,orders,products,stars

origins = [
    "https://a.rcmendez.com",
    "http://localhost:3000", 
]

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(users.router)
app.include_router(cart.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(stars.router)
app.include_router(comments.router)

Base.metadata.create_all(bind=engine)
