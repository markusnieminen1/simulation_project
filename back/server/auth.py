# logic for auth
from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional, Dict, Union
from passlib.context import CryptContext
from pydantic import BaseModel
from db import DB_Connection

import bcrypt
if not hasattr(bcrypt, '__about__'): # fixes a problem with bcrypt.__about__ (4.2.1)
    bcrypt.__about__ = type('about', (object,), {'__version__': bcrypt.__version__})

from dotenv import load_dotenv
load_dotenv()
from os import getenv

ACCESS_SECRET_KEY = str(getenv('access_secret_key'))
REFRESH_SECRET_KEY = str(getenv('refresh_secret_key'))
ACCESS_TOKEN_EXP_MIN = int(getenv('access_token_expiry_in_min'))
REFRESH_TOKEN_EXP_DAY = int(getenv('refresh_token_expiry_in_days'))
TOKEN_ALGORITHM = str(getenv('algorithm'))

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    disabled: bool
    permission_level: int = Optional[None]
    simulation_ids: list = Optional[None]

class UserInDB(User):
    password_hash: str


def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    """ # Description
    Constructs user object from username(email). 
    DB_Connection.fetch_user(user_email=) -> UserInDB(**user_dict)

    Args:
        username (str)

    Returns:
        Optional[UserInDB]: UserInDB -> User object.

                            None if something goes wrong or user not found. 
    """
    with DB_Connection() as conn:
        user_dict = conn.fetch_user(user_email=username)
    if user_dict:
        return UserInDB(**user_dict)
    else:
        return None

def authenticate_user(username: str, password: str) -> Union[User, bool]:
    """ # Description
    Verifies the user exists and the inputted password matches the hashed password. 
    
    Args:
        username (str)
        password (str) (non-hashed)

    Returns:
        Optional[UserInDB]: UserInDB -> User object.

                            None if something goes wrong or user not found. 
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_jwt(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXP_MIN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=ACCESS_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt

def create_refresh_jwt(data: dict):
    pass
