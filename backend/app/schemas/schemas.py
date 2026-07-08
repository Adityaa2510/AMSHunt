import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.asset import AssetType
from app.models.scan import ScanType, ScanStatus
from app.models.finding import FindingType, Severity


class OrganizationCreate(BaseModel):
    name: str
    root_domain: str


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    root_domain: str
    created_at: datetime


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_type: AssetType
    value: str
    is_active: bool
    first_seen: datetime
    last_seen: datetime
    metadata_json: dict


class ScanCreate(BaseModel):
    organization_id: uuid.UUID
    scan_type: ScanType
    target: str


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    scan_type: ScanType
    status: ScanStatus
    target: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_summary: dict


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    asset_id: uuid.UUID
    scan_id: Optional[uuid.UUID] = None
    finding_type: FindingType
    severity: Severity
    title: str
    description: Optional[str] = None
    port: Optional[int] = None
    service: Optional[str] = None
    cve_id: Optional[str] = None
    raw_data: dict
    is_resolved: bool
    discovered_at: datetime


class RiskScoreOut(BaseModel):
    organization_id: uuid.UUID
    score: float
    grade: str
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    calculated_at: datetime
