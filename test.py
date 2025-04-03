# from models import CarCollection, CarModel


# test_car_1= CarModel(brand="ford",make="fiesta",year=2019, cm3=1500, km=120000, price=1000)

# test_car_2= CarModel(brand="fiat", make="stilo",year=2003, cm3=1600, km=320000, price=3000)
# car_list= CarCollection(cars=[test_car_1,test_car_2])


# print(car_list.model_dump())


from fastapi import FastAPI, Form, File, UploadFile
from pathlib import Path
import shutil

app = FastAPI()

# Define the directory where uploaded files will be saved
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload/")
async def upload_file(
    token: str = Form(...),
    file: UploadFile = File(...)
):
    # Construct the file path
    file_path = UPLOAD_DIR / file.filename

    # Save the file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "token": token,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_path": str(file_path)
    }
