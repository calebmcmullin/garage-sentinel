import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import FileResponse, StreamingResponse
import models.file as file_model
from models import User
from db import database
from services import file_services
from services.file_services import storage_path, get_thumbnail
from routes.auth import get_current_user
from routes.users import require_user

router = APIRouter(
    prefix="/api",
    dependencies=[Depends(require_user)]
)

MAX_FILE_SIZE = 250 * 1024 * 1024  # 200 MiB
allowed_types = ["png", "jpg", "jpeg", "mp4"]

async def validate_file(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(400, "Missing filename")

    extension = file.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_types:
        raise HTTPException(415, "Unsupported file format")

    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            f"File too large. Maximum allowed size is {MAX_FILE_SIZE // 1024 ** 2} MB."
        )

    return extension

@router.post("/file", status_code=201)
async def upload_file(request: Request, file: UploadFile = File(...)):
    filename = file.filename
    user = await get_current_user(request)

    if not isinstance(user, User):
        raise HTTPException(status_code=401, detail="Not logged in")

    if not isinstance(filename, str):
        raise HTTPException(status_code=400, detail="Filename missing")

    file_type = await validate_file(file)
    data = await file.read()

    if not isinstance(data, bytes):
        raise HTTPException(status_code=400, detail="File is empty")

    file_id = await file_services.add_file(
        filename=filename,
        user_id=user.id,
        file_type=file_type,
        data=data
    )

    return {"id": file_id}

@router.get("/file/{storage_name}")
async def get_file(storage_name: str, size: str = "original"):
    if not re.fullmatch(r"[0-9a-f]{32}", storage_name):
        raise HTTPException(status_code=400, detail="Invalid storage name")

    file_path = storage_path / storage_name

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    file = await database.get_file_by_storage_name(storage_name)

    if not isinstance(file, file_model.File):
        raise HTTPException(status_code=404, detail="File not found")

    if file.filetype in ["mp4"]:
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            content_disposition_type="inline"
        )

    if size == "thumbnail":
        thumb = get_thumbnail(file_path)

        return StreamingResponse(
            thumb,
            media_type="image/jpeg"
        )

    return FileResponse(
        path=file_path,
        media_type="image/png",
        content_disposition_type="inline"
    )

@router.delete("/file/{storage_name}")
async def delete_file(request: Request, storage_name: str):
    user_id = request.session.get("user_id")

    if not re.fullmatch(r"[0-9a-f]{32}", storage_name):
        raise HTTPException(status_code=400, detail="Invalid storage name")

    file_path = storage_path / storage_name

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    file = await database.get_file_by_storage_name(storage_name)

    if not isinstance(file, file_model.File):
        raise HTTPException(status_code=404, detail="File not found")

    # Reject deletion of another user's file
    if file.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this file"
        )

    return await file_services.delete_user_file(user_id, storage_name)

@router.get("/photos")
async def get_photos(request: Request):
    user = await get_current_user(request)

    if not isinstance(user, User):
        raise HTTPException(
            status_code=401,
            detail="Not logged in",
        )

    photos = await file_services.get_files(user.id)
    return photos

@router.get("/videos")
async def get_videos(request: Request):
    user = await get_current_user(request)

    if not isinstance(user, User):
        raise HTTPException(
            status_code=401,
            detail="Not logged in",
        )

    videos = await file_services.get_files(user.id, file_types=["mp4"])
    return videos