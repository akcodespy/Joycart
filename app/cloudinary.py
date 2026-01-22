import time, cloudinary, cloudinary.utils, os
from fastapi import APIRouter

router = APIRouter()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)

@router.get("/cloudinary/sign")
def sign_upload(folder: str):
    timestamp = int(time.time())

    params = {
        "timestamp": timestamp,
        "folder": folder,
    }

    signature = cloudinary.utils.api_sign_request(
        params,
        os.getenv("API_SECRET")
    )

    return {
        "timestamp": timestamp,
        "signature": signature,
        "api_key": os.getenv("API_KEY"),
        "cloud_name": os.getenv("CLOUD_NAME"),
        "folder": folder,
    }
