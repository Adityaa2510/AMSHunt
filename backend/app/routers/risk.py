import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.schemas import RiskScoreOut
from app.services.risk_score import calculate_risk_score

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/{organization_id}", response_model=RiskScoreOut)
async def get_risk_score(organization_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await calculate_risk_score(db, organization_id)
