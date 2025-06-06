from fastapi import APIRouter, Body, Request, status

# from models import UserModel
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from authentication import AuthHandler
from models import CurrentUserModel, LoginModel, UserModel


router = APIRouter()
auth_handler = AuthHandler()


@router.post("/register", response_description="Register user")
async def register(request: Request, newUser: LoginModel = Body(...)) -> UserModel:
    users = request.app.db["users"]

    # Hash the password before inserting it into MongoDB

    newUser.password = auth_handler.get_password_hash(newUser.password)
    newUser = newUser.model_dump()

    # check existing user or email 409 Conflict:

    existing_username = await users.find_one({"username": newUser["username"]})
    # check if the username exist
    if existing_username is not None:
        # return "The password and the username are not recognized"
        raise HTTPException(
            status_code=409,
            detail=f"User with username {newUser['username']} and password already exist",
        )
    newUser = await users.insert_one(newUser)
    create_user = await users.find_one({"_id": newUser.inserted_id})
    return create_user

    # return print(f"{existing_username}")


@router.post("/login", response_description="Login user")

async def login(request: Request, loginUser: LoginModel = Body(...)):
    #first get the connexion element or we can put it in the depends
    users=request.app.db["users"]
    #find the user
    user= await users.find_one({"username": loginUser.username})
    #check if the user password or the user variable is empty or different
    check_password = auth_handler.verify_password(loginUser.password, user["password"])
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username and / or password")
    
    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid username and / or password")
    #if every thing is ok generate the token
    token = auth_handler.encode_token(str(user["_id"]),user["username"])
    response=JSONResponse(content={

        "token":token,
        "username":user["username"]
    })
    return response
    # return {
    #     "token":token,
    #     "username":user["username"]
    # }


@router.get("/me", response_description=" Logged in user data", response_model=CurrentUserModel)
async def me (request:Request, response:Response, user_data=Depends(auth_handler.auth_wrapper)):
    users=request.app.db["users"]
    currentUser = await users.find_one(
        {"_id":ObjectId(user_data["user_id"])}
    )

    if not currentUser:
        return HTTPException(status_code=401, detail="User does not exist")

    return currentUser
