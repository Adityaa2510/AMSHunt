import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.asset import Organization, Asset
from app.schemas.schemas import OrganizationCreate, OrganizationOut, AssetOut

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationOut)
async def create_organization(payload: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    org = Organization(name=payload.name, root_domain=payload.root_domain)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/", response_model=list[OrganizationOut])
async def list_organizations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization))
    return result.scalars().all()


@router.get("/{org_id}", response_model=OrganizationOut)
async def get_organization(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/{org_id}/assets", response_model=list[AssetOut])
async def list_assets(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.organization_id == org_id))
    return result.scalars().all()
