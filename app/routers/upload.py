from fastapi import APIRouter
from app import schemas

router = APIRouter(prefix="/upload-grades", tags=["Upload"])

# @router.post("/", responce_model=schemas.StudentCreate)