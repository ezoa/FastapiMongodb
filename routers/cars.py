from fastapi import (
    APIRouter,
    Body,
    Request,
    status,
    HTTPException,
    Depends,
    Response,
    File,
    Form,
    UploadFile,
)
from models import CarModel, CarCollection, UpdateCarModel, CarCollectionPagination
from bson import ObjectId, Binary
from authentication import AuthHandler
from pymongo import ReturnDocument
import cloudinary
from cloudinary import uploader
from fastapi.responses import JSONResponse

from pathlib import Path

router = APIRouter()
CARS_PER_PAGE = 10
auth_handler = AuthHandler()


# Directory to save uploaded images
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the folder exists


@router.post(
    "/",
    response_description="Add new car",
    response_model=CarModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def add_car(request: Request, car: CarModel = Body(...)):
    # Access the "cars" collection from the MongoDB database

    cars = request.app.db["cars"]

    # Convert the CarModel object to a dictionary, using aliases for field names.
    # Exclude the "id" field to avoid conflicts since MongoDB will generate its own "_id".

    document = car.model_dump(by_alias=True, exclude=["id"])
    # Insert the new document into the "cars" collection and get the inserted document's ID
    inserted = await cars.insert_one(document)

    # Retrieve and return the newly inserted document using the generated "_id"
    return await cars.find_one({"_id": inserted.inserted_id})


@router.post(
    "/AddCar",
    response_description="Add new car with picture",
    response_model=CarModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_car_with_picture(
    request: Request,
    brand: str = Form("brand"),
    make: str = Form("make"),
    year: str = Form("year"),
    cm3: int = Form("cm3"),
    km: int = Form("km"),
    price: int = Form("price"),
    picture: UploadFile = File(...),
):
    try:

        cloudinary_image=cloudinary.uploader.upload(

            picture.file,folder="FARM2", crop="fill",width=800
        )
        picture_url= cloudinary_image["url"]


        car= CarModel(brand=brand, make=make, year=year, cm3=cm3, km=km, price=price, picture_url=picture_url)
        cars= request.app.db["cars"]
        document= car.model_dump(by_alias= True, exclude=["id"])
        inserted= await cars.insert_one(document)
        return await cars.find_one({"_id": inserted.inserted_id})
        # file_extension= picture.filename.split(".")[-1]
        # file_name=f"{ObjectId()}.{file_extension}"
        # file_path= UPLOAD_DIR/file_name




        # # Save the upload image to the floor 
        # with file_path.open("wb") as f:
        #     f.write(await picture.read())

        # # Construct the image URL
        # picture_url=f"http://127.0.0.1:8000/cars/images/{file_name}"

        # car= CarModel(brand=brand, make=make, year=year, cm3=cm3, km=km, price=price,picture_url=picture_url)
        # cars= request.app.db["cars"]
        # document= car.model_dump(by_alias= True, exclude=["id"])
        # inserted= await cars.insert_one(document)
        # return await cars.find_one({"_id": inserted.inserted_id})
        # # return CarModel(id=str(inserted.inserted_id), **car)

    except UnicodeDecodeError as e:
        return JSONResponse(status_code=400, content={"message":"invalid image format. Ensure the uploaded file isvalid image "})

# @router.post(
#     "/addcar",
#     response_description="Add new car with picture",
#     response_model=CarModel,
#     status_code=status.HTTP_201_CREATED,
# )
# async def add_car_with_picture(
#     request: Request,
#     brand: str = Form("brand"),
#     make: str = Form("make"),
#     year: int = Form("year"),
#     cm3: int = Form("cm3"),
#     km: int = Form("km"),
#     price: int = Form("price"),
#     picture: UploadFile = File(...),
# ):
#     try:
#         # Validate that the uploaded file is an image
#         if not picture.content_type.startswith("image/"):
#             raise HTTPException(status_code=400, detail="Invalid file format. Upload an image.")

#         # # Generate a unique filename
#         file_extension = picture.filename.split(".")[-1]
#         file_name = f"{ObjectId()}.{file_extension}"
#         file_path = UPLOAD_DIR / file_name

#         # # Save the uploaded image to disk
#         content = await picture.read()  # Read file bytes once
#         with file_path.open("wb") as f:
#             f.write(content)
        
#         # # Construct the image URL
#         picture_url = f"http://127.0.0.1:8000/cars/images/{file_name}"

#         # # Create the CarModel instance (note: ensure CarModel does not include any field for raw image bytes)
#         car = CarModel(
#             brand=brand,
#             make=make,
#             year=year,
#             cm3=cm3,
#             km=km,
#             price=price,
#             picture_url=picture_url,
#         )

#         # # Dump the model to a dict, excluding 'id' so that MongoDB generates it
#         document = car.model_dump(by_alias=True, exclude={"id"})
#         cars = request.app.db["cars"]
#         inserted = await cars.insert_one(document)
#         car.id=inserted.inserted_id
#         return car

#         # # Return the CarModel with the generated id, using model_dump() to ensure only JSON-serializable data is returned
#         # # return CarModel(id=str(inserted.inserted_id), **car.model_dump())
#         # return "thank You"
    
#     except UnicodeDecodeError:
#         return JSONResponse(
#             status_code=400,
#             content={"message": "Invalid image format. Ensure the uploaded file is a valid image."}
#         )
# @router.get("/",response_description="List all cars", response_model=CarCollection, response_model_by_alias=False)

# async def list_cars(request: Request):
#     # Access the "cars" collection from the MongoDB database
#     cars=request.app.db["cars"]
#     # results=[]

#     # cursor=cars.find()
#     # async for document in cursor:
#     #     results.append(document)

#     # return CarCollection(cars=results)
#     # Retrieve up to 1000 car documents from the database and return as a CarCollection
#     return CarCollection(cars=await cars.find().to_list(1000))


@router.get(
    "/",
    response_description="List all cars, paginated",
    response_model=CarCollectionPagination,
    response_model_by_alias=False,
)
async def list_cars(request: Request, page: int = 1, limit: int = CARS_PER_PAGE):

    cars = request.app.db["cars"]
    results = []
    cursor = cars.find().limit(limit).skip((page - 1) * limit)
    total_documents = await cars.count_documents({})
    has_more = total_documents > limit * page
    async for document in cursor:
        results.append(document)
    return CarCollectionPagination(cars=results, page=page, has_more=has_more)


@router.get(
    "/{id}",
    response_description="Get a single car by ID",
    response_model=CarModel,
    response_model_by_alias=False,
)
async def show_car(id: str, request: Request):
    # Get the "cars" collection from the database
    cars = request.app.db["cars"]
    try:
        # Convert the string ID to a MongoDB ObjectId
        id = ObjectId(id)

    except Exception:
        # If the ID is not a valid ObjectId, raise a 404 error

        raise HTTPException(status_code=404, detail=f"Car {id} not found")
    # if (car := await cars.find_one({"_id": ObjectId(id)})) is not None:
    #     return car

    # raise HTTPException(status_code=404,detail=f"Car eith {id} not found")
    # Query the database for a car with the given _id
    car = await cars.find_one({"_id": ObjectId(id)})

    if car is not None:
        return car
    raise HTTPException(status_code=404, detail=f"Car with {id} not found")


@router.put(
    "/{id}",
    response_description=" Update the car",
    response_model=CarModel,
    response_model_by_alias=False,
)
async def update_car(
    id: str,
    request: Request,
    user=Depends(auth_handler.auth_wrapper),
    car: UpdateCarModel = Body(...),
):
    # Access the "cars" collection from the database
    cars = request.app.db["cars"]
    try:
        # convert the provided id from a string to MongoDb objectId
        id = ObjectId(id)

    except Exception:
        # if conversion fails, return a 404 error (invalid id format)
        raise HTTPException(status_code=404, detail=f"car {id } not found")

    car = {
        k: v
        for k, v in car.model_dump(by_alias=True).items()
        if v is not None and k != "_id"
    }
    if len(car) >= 1:
        cars = request.app.db["cars"]
        update_result = await cars.find_one_and_update(
            {"_id": id},  # Find car by its ID
            {"$set": car},  # Update only the provided fields
            return_document=ReturnDocument.AFTER,
        )
    if update_result is not None:
        return update_result
    else:
        raise HTTPException(status_code=404, detail=f"Car{id} not found")


@router.delete("/{id}", response_description="Delete a car")
async def delete_car(
    id: str, request: Request, user=Depends(auth_handler.auth_wrapper)
):
    # async def delete_car(id:str, request:Request):
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"car {id} not found")

    cars = request.app.db["cars"]
    delete_result = await cars.delete_one({"_id": id})
    if delete_result.deleted_count == 1:

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Car with {id} not found")
