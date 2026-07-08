"""
Risk scoring: converts raw findings into a single 0-100 exposure score,
weighted by severity, then bucketed into a letter grade for the executive
report. Weights are simple/transparent by design (easy to explain and
defend) rather than a black-box model.
"""
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finding import Finding, Severity
from app.models.asset import Asset

SEVERITY_WEIGHTS = {
    Severity.critical: 25,
    Severity.high: 12,
    Severity.medium: 5,
    Severity.low: 2,
    Severity.info: 0,
}

MAX_SCORE = 100


def _grade_for_score(score: float) -> str:
    if score >= 80:
        return "F"
    if score >= 60:
        return "D"
    if score >= 40:
        return "C"
    if score >= 20:
        return "B"
    return "A"


async def calculate_risk_score(db: AsyncSession, organization_id) -> dict:
    counts_query = (
        select(Finding.severity, func.count(Finding.id))
        .join(Asset, Finding.asset_id == Asset.id)
        .where(Asset.organization_id == organization_id, Finding.is_resolved.is_(False))
        .group_by(Finding.severity)
    )
    rows = (await db.execute(counts_query)).all()
    counts = {sev: 0 for sev in Severity}
    for severity, count in rows:
        counts[severity] = count

    raw_score = sum(SEVERITY_WEIGHTS[sev] * counts[sev] for sev in Severity)
    # Soft cap via exponential decay so a handful of findings doesn't instantly max the score,
    # while the score still climbs meaningfully with real exposure.
    normalized = MAX_SCORE * (1 - pow(0.9, raw_score / 5)) if raw_score > 0 else 0
    normalized = round(min(normalized, MAX_SCORE), 1)

    return {
        "organization_id": organization_id,
        "score": normalized,
        "grade": _grade_for_score(normalized),
        "critical_count": counts[Severity.critical],
        "high_count": counts[Severity.high],
        "medium_count": counts[Severity.medium],
        "low_count": counts[Severity.low],
        "info_count": counts[Severity.info],
        "calculated_at": datetime.now(timezone.utc),
    }
