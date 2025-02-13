# The actual API 
from fastapi import FastAPI, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from auth import create_access_jwt, create_refresh_jwt, Token, RefreshToken, authenticate_user, get_password_hash, get_user
from db import DB_Connection
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from os import getenv
from uvicorn import run


ACCESS_PUBLIC_KEY = getenv('access_public_key')
REFRESH_PUBLIC_KEY = getenv('refresh_public_key')
TOKEN_ALGORITHM = getenv('algorithm')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=[True],
    allow_methods=["*"],
    allow_headers=["*"]
)

db = DB_Connection()


@app.get('/')
async def root():
    return {"message": "test"}

@app.post("/login", response_model=RefreshToken, status_code=status.HTTP_200_OK)
async def login_for_tokens(
    form_data: Annotated[
        OAuth2PasswordRequestForm, 
        Depends()],
        ) -> RefreshToken:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sim_ids = None
    if user.simulation_ids:
        sim_ids = user.simulation_ids
    access_token = create_access_jwt(data={"sub": user.username, "simulation_ids": sim_ids})
    refresh_token = create_refresh_jwt(data={"sub": user.username, "simulation_ids": sim_ids})
    
    return RefreshToken(access_token=access_token, token_type="Bearer", refresh_token=refresh_token)
    

@app.post("/login/refresh")
async def access_token_refresh(refresh_token:str):
    pass

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=RefreshToken)
async def register_user(form_data: 
            Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    with db:
        data_in_db = db.fetch_password_hash(form_data.username)
        
        if data_in_db: # String or None
            raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Email already in use",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            userdata = [{"username": form_data.username, "password_hash":get_password_hash(form_data.password)}]
            data_in_db = db.insert_data('users', userdata)
            if not data_in_db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error while inserting user data",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    user = authenticate_user(form_data.username, form_data.password)
    sim_ids = None
    if user.simulation_ids:
        sim_ids = user.simulation_ids
    access_token = create_access_jwt(data={"sub": user.username, "simulation_ids": sim_ids})
    refresh_token = create_refresh_jwt(data={"sub": user.username, "simulation_ids": sim_ids})
    
    return RefreshToken(access_token=access_token, token_type="Bearer", refresh_token=refresh_token)
            

async def get_current_user(access_token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, ACCESS_PUBLIC_KEY, algorithms=[TOKEN_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/protected-route")
async def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}! This is a protected route."}


if __name__ == "__main__":
    run("server:app", host='0.0.0.0' ,port=8000, reload=True, access_log=True)