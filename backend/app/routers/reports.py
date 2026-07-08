import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.asset import Organization, Asset
from app.models.finding import Finding, Severity
from app.services.risk_score import calculate_risk_score

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{organization_id}/executive-summary")
async def executive_summary(organization_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Structured executive-summary payload: risk score, asset counts, top
    findings, and a plain-language narrative. Frontend renders this directly;
    a PDF export (e.g. via ReportLab) can consume the same JSON.
    """
    org = await db.get(Organization, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    risk = await calculate_risk_score(db, organization_id)

    asset_count = (await db.execute(
        select(func.count(Asset.id)).where(Asset.organization_id == organization_id)
    )).scalar_one()

    top_findings_q = (
        select(Finding)
        .join(Asset, Finding.asset_id == Asset.id)
        .where(Asset.organization_id == organization_id, Finding.is_resolved.is_(False))
        .where(Finding.severity.in_([Severity.critical, Severity.high]))
        .order_by(Finding.discovered_at.desc())
        .limit(10)
    )
    top_findings = (await db.execute(top_findings_q)).scalars().all()

    narrative = (
        f"{org.name}'s external attack surface currently spans {asset_count} discovered assets, "
        f"scoring {risk['score']}/100 (Grade {risk['grade']}) on exposure risk. "
        f"There are {risk['critical_count']} critical and {risk['high_count']} high-severity "
        f"findings requiring attention. Immediate remediation of critical findings is recommended."
    )

    return {
        "organization": {"id": str(org.id), "name": org.name, "root_domain": org.root_domain},
        "risk": risk,
        "asset_count": asset_count,
        "top_findings": [
            {"title": f.title, "severity": f.severity, "cve_id": f.cve_id, "discovered_at": f.discovered_at.isoformat()}
            for f in top_findings
        ],
        "narrative": narrative,
    }
