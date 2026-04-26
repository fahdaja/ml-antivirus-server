from fastapi import Form
from app.features.scans.schema import ScanHistoryResponse
from app.features.scans.service import get_scan_history
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db # Assuming get_db dependency exists
from app.features.scans.schema import ScanResponse
from app.features.scans.service import scan_file_and_save, delete_scan

router = APIRouter(
    prefix="/api/v1",
    tags=["scans"],
    responses={404: {"description": "Not found"}},
)

@router.post("/scan", response_model=ScanResponse)
async def upload_and_scan(
    file: UploadFile = File(...),
    app_platform: str = Form("unknown"),
    db: Session = Depends(get_db)
):
    """
    Upload a file, run it through the ML model, and save the scan result.
    If the file hash already exists, it returns the existing data instead.
    """
    scan_result = await scan_file_and_save(db, file, app_platform)
    return scan_result

@router.delete("/{scan_id}")
def delete_scan_data(
    scan_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a scan result manually based on ID.
    """
    return delete_scan(db, scan_id)

@router.get("/history", response_model=ScanHistoryResponse)
def read_scan_history(
    skip: int = 0, 
    limit: int = 10, 
    app_platform:str = None,
    db: Session = Depends(get_db)
):
    """
    Mengambil riwayat scan dengan sistem pagination.
    - skip: jumlah data yang dilewati (default 0)
    - limit: jumlah data yang diambil (default 10)
    """
    return get_scan_history(db, skip=skip, limit=limit, app_platform=app_platform)
