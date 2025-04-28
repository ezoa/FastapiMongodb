# import datetime
# import jwt
# from fastapi import HTTPException, Security
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# from passlib.context import CryptContext


# class AuthHandler:
#     security = HTTPBearer()
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     secret = "FARMSTACKsecretString"


#     # hash the password

#     def get_password_hash(self, password: str) -> str :
#         return self.pwd_context.hash(password)

#     #verify the password

#     def verify_password(self, plain_password: str, hashed_password: str)-> bool:
#         return self.pwd_context.verify(plain_password, hashed_password)

#     def encode_token(self, user_id: int, username: str )-> str:
#         payload={

#             "exp": datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=30),
#             "iat": datetime.datetime.now(datetime.timezone.utc),
#             "sub": {"user_id": user_id, "username": username},
#             # "sub": f"{user_id}_{username}",


#         }
#         return jwt.encode(payload, self.secret, algorithm="HS256")

#     def decode_token(self, token: str)->str:
#         try:
#             payload = jwt.decode(
#                 token,
#                 self.secret,
#                 algorithms=["HS256"],


#             )
#             return payload["sub"]
#         except jwt.ExpiredSignatureError:

#             raise HTTPException(

#                 status_code=401,
#                 detail="Signature has expired"
#             )
#         except jwt.InvalidTokenError:
#             raise HTTPException(

#                 status_code=401,
#                 detail="invalid token"
#             )


#     def auth_wrapper(

#             self,
#             auth: HTTPAuthorizationCredentials = Security(security)
#     )-> dict:
#         return self.decode_token(auth.credentials)

# import datetime

# import jwt
# from fastapi import HTTPException, Security
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer,OAuth2AuthorizationCodeBearer,OAuth2PasswordRequestForm
# from passlib.context import CryptContext


# class AuthHandler:
#     security = HTTPBearer()
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     secret = "FARMSTACKsecretString"


#     def get_password_hash(self, password):
#         return self.pwd_context.hash(password)

#     def verify_password(self, plain_password, hashed_password):
#         return self.pwd_context.verify(plain_password, hashed_password)

#     def encode_token(self, user_id:str, username:str):
#         payload = {
#             "exp": datetime.datetime.now(datetime.timezone.utc)
#             + datetime.timedelta(minutes=30),
#             "iat": datetime.datetime.now(datetime.timezone.utc),
#             # "sub": user_id,
#             # "username": username
#             "sub":{
#                 "user_id": user_id,
#              "username": username
#             }
#         }
#         return jwt.encode(payload, self.secret, algorithm="HS256")

#     def decode_token(self, token):
#         try:
#             payload = jwt.decode(token, self.secret, algorithms=["HS256"])
#             print("Decoded JWT Payload:", payload)
#             return payload["sub"]
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="Signature has expired")
#         except jwt.InvalidTokenError:
#             raise HTTPException(status_code=401, detail="Invalid token")

#     def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
#         return self.decode_token(auth.credentials)


import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Annotated
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthHandler:

    algorithm = "HS256"
    pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_TIME = 40

    def get_password_hash(self, plain_password: str):
        return self.pass_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pass_context.verify(plain_password, hashed_password)

    def create_encode_token(self, data: dict, expired_time: timedelta | None = None):
        data_dict = data.copy()
        if expired_time:
            expire_time = datetime.now(timezone.utc) + expired_time

        else:
            expire_time = datetime.now(timezone.utc) + timedelta(
                minutes=self.ACCESS_TOKEN_EXPIRE_TIME
            )

        data_dict.update({"exp": expire_time})

        return jwt.encode(data_dict, self.SECRET_KEY, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.algorithm])
            return payload
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="token not valid")



    def auth_wrapper(self, token: Annotated[str, Depends(oauth2_scheme)]):
        
        return self.decode_token(token)