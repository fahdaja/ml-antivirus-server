from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base # Assuming this is your database declarative base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True) # Could be filename, file hash, or specific data
    file_hash = Column(String, index=True) # Result, e.g., 'benign', 'malware'
    file_size = Column(Integer, index=True)
    app_platform = Column(String, index=True)
    status = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, index=True)
    prediction = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
