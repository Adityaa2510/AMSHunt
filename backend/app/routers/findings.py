import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.finding import Finding, Severity
from app.models.asset import Asset
from app.schemas.schemas import FindingOut

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("/", response_model=list[FindingOut])
async def list_findings(
    organization_id: uuid.UUID | None = None,
    severity: Severity | None = None,
    is_resolved: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Finding)
    if organization_id:
        query = query.join(Asset, Finding.asset_id == Asset.id).where(Asset.organization_id == organization_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if is_resolved is not None:
        query = query.where(Finding.is_resolved == is_resolved)

    result = await db.execute(query.order_by(Finding.discovered_at.desc()))
    return result.scalars().all()


@router.patch("/{finding_id}/resolve", response_model=FindingOut)
async def resolve_finding(finding_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    finding = await db.get(Finding, finding_id)
    finding.is_resolved = True
    await db.commit()
    await db.refresh(finding)
    return finding
