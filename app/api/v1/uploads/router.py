from fastapi import APIRouter, File, UploadFile, HTTPException, status
import os
from app.services.file_storage import save_uploaded_image
from starlette.responses import FileResponse
from typing import Annotated
from fastapi.responses import HTMLResponse

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
    saved = save_uploaded_image(file)

    return {
        "filename": saved["filename"],
        "content_type": saved["content_type"],
        "url": saved["url"],
        # "size": saved["size"],
        # "chunks_size_used": saved["chunks_size_used"],
        # "chunk_calls": saved["chunk_calls"] ,
        # "chunk_size_sample": saved["chunk_size_sample"]
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

@router.post("/files/")
async def create_files(files: Annotated[list[bytes], File()]):
    return {"file_sizes": [len(file) for file in files]}


@router.post("/uploadfiles/")
async def create_upload_files(files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    return {"filenames": [file.filename for file in files]}

@router.get("/")
async def main():
    content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Subida de Archivos</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }

            body {
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: #f4f6f9;
                padding: 20px;
            }

            .container {
                width: 100%;
                max-width: 500px;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }

            h1 {
                text-align: center;
                margin-bottom: 25px;
                color: #333;
            }

            .form-card {
                margin-bottom: 20px;
                padding: 20px;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                background: #fafafa;
            }

            .form-card h2 {
                font-size: 16px;
                margin-bottom: 15px;
                color: #555;
            }

            input[type="file"] {
                width: 100%;
                margin-bottom: 15px;
                padding: 10px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
            }

            button {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 6px;
                background: #2563eb;
                color: white;
                font-size: 15px;
                cursor: pointer;
                transition: background 0.3s;
            }

            button:hover {
                background: #1d4ed8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Subida de Archivos</h1>

            <div class="form-card">
                <h2>Endpoint /files/</h2>
                <form action="/files/" enctype="multipart/form-data" method="post">
                    <input name="files" type="file" multiple>
                    <button type="submit">
                        Subir archivos
                    </button>
                </form>
            </div>

            <div class="form-card">
                <h2>Endpoint /upload/uploadfiles/</h2>
                <form action="/upload/uploadfiles/" enctype="multipart/form-data" method="post">
                    <input name="files" type="file" multiple>
                    <button type="submit">
                        Subir archivos
                    </button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)