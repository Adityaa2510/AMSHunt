import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scan import Scan, ScanType, ScanStatus
from app.models.asset import Asset
from app.schemas.schemas import ScanCreate, ScanOut
from app.workers.tasks import (
    run_discovery_scan, run_port_scan, run_tech_and_ssl_scan, run_vuln_scan_task,
)

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/", response_model=ScanOut)
async def create_scan(payload: ScanCreate, db: AsyncSession = Depends(get_db)):
    scan = Scan(
        organization_id=payload.organization_id,
        scan_type=payload.scan_type,
        target=payload.target,
        status=ScanStatus.queued,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    if payload.scan_type == ScanType.discovery:
        task = run_discovery_scan.delay(str(scan.id), str(payload.organization_id), payload.target)
    else:
        # Non-discovery scans operate on a specific asset; it must already exist.
        asset = (await db.execute(
            select(Asset).where(
                Asset.organization_id == payload.organization_id, Asset.value == payload.target
            )
        )).scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=400,
                detail="Target must be a known asset. Run a discovery scan first or register the asset.",
            )

        if payload.scan_type == ScanType.port_scan:
            task = run_port_scan.delay(str(scan.id), str(asset.id), payload.target)
        elif payload.scan_type == ScanType.tech_detect:
            url = payload.target if payload.target.startswith("http") else f"https://{payload.target}"
            task = run_tech_and_ssl_scan.delay(str(scan.id), str(asset.id), url, payload.target)
        elif payload.scan_type == ScanType.vuln_scan:
            url = payload.target if payload.target.startswith("http") else f"https://{payload.target}"
            task = run_vuln_scan_task.delay(str(scan.id), str(asset.id), url)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported scan_type: {payload.scan_type}")

    scan.celery_task_id = task.id
    await db.commit()
    await db.refresh(scan)
    return scan


@router.get("/", response_model=list[ScanOut])
async def list_scans(organization_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Scan)
    if organization_id:
        query = query.where(Scan.organization_id == organization_id)
    result = await db.execute(query.order_by(Scan.created_at.desc()))
    return result.scalars().all()


@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan(scan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    scan = await db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
