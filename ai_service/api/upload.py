from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.postgres import get_db
from services.upload_service import UploadService


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


class UploadRequest(BaseModel):

    vehicle_id: int


@router.post("/")
def upload(
    request: UploadRequest,
    db: Session = Depends(get_db)
):

    service = UploadService(db)

    result = service.process_upload(
        vehicle_id=request.vehicle_id
    )

    return result