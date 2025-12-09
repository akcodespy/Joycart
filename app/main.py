from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db import Base, engine

Base.metadata.create_all(bind = engine)

app = FastAPI()
app.mount('/static',  StaticFiles(directory='static'), name = 'static')

@app.get('/')
def home():
    return FileResponse("static/homepage.html")
@app.get('/login')
def login():
    return FileResponse("static/login.html")
@app.get("/register")
def register():
    return FileResponse("static/register.html")
@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")

