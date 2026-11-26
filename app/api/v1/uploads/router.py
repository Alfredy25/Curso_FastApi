from fastapi import APIRouter, File, UploadFile, HTTPException, status
import os
import shutil
import uuid
from pathlib import Path

from starlette.responses import FileResponse

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "app/media/"

@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)):
    return {
        "filename": "archivo_subido",
        "size_bytes": len(file)
    }


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }

@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpg", "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imágenes PNG, JPG o JPEG"
        )
    ext = Path(file.filename).suffix
    # ext = os.path.splitext(file.filename)[1] # .png # .jpeg
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}"
    }

@router.get("/api/fotos/{foto_id}")
async def get_foto(foto_id: str):
    file_path = os.path.join(MEDIA_DIR, foto_id)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="archivo no encontrado"
        )
    return FileResponse(file_path, media_type="image/jpg")
