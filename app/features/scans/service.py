from sqlalchemy.sql import desc
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import numpy as np
import os
import hashlib
from app.features.scans.model import Scan, ScanResult
from app.features.scans.schema import ScanResponse
from app.ml.engine import get_ort_session, extract_features

async def scan_file_and_save(db: Session, file: UploadFile, app_platform: str) -> ScanResponse:
    # 1. Read file and calculate hash
    file_bytes = await file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # 2. Check if file already exists
    existing_scan = db.query(Scan).filter(Scan.file_hash == file_hash).first()
    if existing_scan:
        existing_result = db.query(ScanResult).filter(ScanResult.scan_id == existing_scan.id).first()
        existing_scan.prediction = existing_result.prediction if existing_result else None
        return existing_scan

    # 3. Save file temporarily
    temp_dir = "/tmp/scans"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
            
        # 4. Extract features & predict
        input_data = extract_features(file_path)
        ort_sess = get_ort_session()
        input_name = ort_sess.get_inputs()[0].name
        raw_result = ort_sess.run(None, {input_name: input_data})
        
        # Convert prediction result safely
        output_array = np.array(raw_result[0])
        flat_list = output_array.flatten().tolist()
        
        # Handle case where model outputs literal strings directly (e.g. ['malware'] or ['benign'])
        if len(flat_list) > 0 and isinstance(flat_list[0], str):
            label_str = flat_list[0].lower()
            predicted_label = "malware" if "malware" in label_str else "benign"
        else:
            # Handle case where output is numbers (e.g., [0, 1] one-hot/logits or single [1])
            if len(flat_list) > 1:
                predicted_class_idx = np.argmax(flat_list)
            else:
                predicted_class_idx = int(round(flat_list[0]))
            predicted_label = "malware" if predicted_class_idx == 1 else "benign"
        
        # 5. Save to Database
        db_scan = Scan(
            filename=file.filename,
            file_hash=file_hash,
            file_size=len(file_bytes),
            app_platform=app_platform,
            status="completed"
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        
        db_result = ScanResult(
            scan_id=db_scan.id,
            prediction=predicted_label
        )
        db.add(db_result)
        db.commit()
        
        # Dynamic attribute for pydantic response model
        db_scan.prediction = predicted_label
        return db_scan
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Scanning failed: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

def delete_scan(db: Session, scan_id: int):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan data not found")
        
    scan_result = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).first()
    if scan_result:
        db.delete(scan_result)
        
    db.delete(scan)
    db.commit()
    return {"message": "Data deleted successfully"}

def get_scan_history(db: Session, skip: int = 0, limit: int = 10):
    # Query dasar dengan Join
    query = db.query(Scan).order_by(desc(Scan.created_at))
    
    total = query.count()
    scans = query.offset(skip).limit(limit).all()

    # Memasukkan hasil prediksi secara dinamis ke objek Scan
    for scan in scans:
        result = db.query(ScanResult).filter(ScanResult.scan_id == scan.id).first()
        scan.prediction = result.prediction if result else "unknown"

    return {
        "total": total,
        "page": (skip // limit) + 1,
        "size": len(scans),
        "items": scans
    }
