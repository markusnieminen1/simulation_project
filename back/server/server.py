# The actual API 
from fastapi import FastAPI, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import create_access_jwt, Token, TokenData, User, get_user, authenticate_user
from db import DB_Connection
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from os import getenv


ACCESS_SECRET_KEY = getenv('access_secret_key')
TOKEN_ALGORITHM = getenv('algorithm')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
db = DB_Connection()

@app.get('/')
async def root():
    return {"message": "test"}

@app.post("/login")
async def login_for_access_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm, 
        Depends()],
        ) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_jwt(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

@app.post("/refresh-token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    pass


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user('fake_users_db_remove_quotes', username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user