from uuid import uuid4

from fastapi import UploadFile
from minio import Minio

from core.config import settings
from storage.minio import minio_client


async def upload_file(file: UploadFile, folder: str) -> str:

    extension = ""

    if file.filename and "." in file.filename:
        extension = "." + file.filename.split(".")[-1]

    object_name = f"{folder}/{uuid4()}{extension}"

    file_size = 0
    data = await file.read()
    file_size = len(data)

    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        data=__import__("io").BytesIO(data),
        length=file_size,
        content_type=file.content_type or "application/octet-stream",
    )

    return "http://localhost:9000/media/" + object_name