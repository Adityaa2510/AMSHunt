"""
Celery tasks that run the scan pipeline. Each task is sync (Celery's native
mode) but drives the async tool wrappers via asyncio.run(), and opens its
own short-lived DB session rather than sharing one across tasks.
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.asset import Asset, AssetType
from app.models.finding import Finding, FindingType, Severity

from app.services.discovery import discover_subdomains, resolve_live_hosts
from app.services.port_scan import scan_ports
from app.services.tech_detect import detect_technologies
from app.services.ssl_check import inspect_ssl
from app.services.vuln_scan import run_vuln_scan


def _run_async(coro):
    return asyncio.run(coro)


async def _mark_scan(db: AsyncSession, scan_id: uuid.UUID, **fields):
    scan = await db.get(Scan, scan_id)
    for k, v in fields.items():
        setattr(scan, k, v)
    await db.commit()


async def _upsert_asset(db: AsyncSession, org_id: uuid.UUID, asset_type: AssetType, value: str) -> Asset:
    existing = (await db.execute(
        select(Asset).where(Asset.organization_id == org_id, Asset.value == value)
    )).scalar_one_or_none()
    if existing:
        existing.last_seen = datetime.utcnow()
        await db.commit()
        return existing
    asset = Asset(organization_id=org_id, asset_type=asset_type, value=value)
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


async def _save_finding(db: AsyncSession, asset_id, scan_id, **fields):
    finding = Finding(asset_id=asset_id, scan_id=scan_id, **fields)
    db.add(finding)
    await db.commit()


@celery_app.task(name="asm.run_discovery_scan", bind=True)
def run_discovery_scan(self, scan_id: str, organization_id: str, root_domain: str):
    async def _do():
        async with AsyncSessionLocal() as db:
            await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.running, started_at=datetime.utcnow())
            try:
                subdomains = await discover_subdomains(root_domain)
                live_hosts = await resolve_live_hosts(subdomains)

                for host_info in live_hosts:
                    host = host_info.get("input") or host_info.get("host")
                    if not host:
                        continue
                    await _upsert_asset(db, uuid.UUID(organization_id), AssetType.subdomain, host)

                await _mark_scan(
                    db, uuid.UUID(scan_id),
                    status=ScanStatus.completed, finished_at=datetime.utcnow(),
                    result_summary={"subdomains_found": len(subdomains), "live_hosts": len(live_hosts)},
                )
            except Exception as e:
                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.failed,
                                  finished_at=datetime.utcnow(), error_message=str(e))
                raise
    _run_async(_do())


@celery_app.task(name="asm.run_port_scan", bind=True)
def run_port_scan(self, scan_id: str, asset_id: str, target: str):
    async def _do():
        async with AsyncSessionLocal() as db:
            await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.running, started_at=datetime.utcnow())
            try:
                result = await scan_ports(target)
                for p in result["ports"]:
                    await _save_finding(
                        db, uuid.UUID(asset_id), uuid.UUID(scan_id),
                        finding_type=FindingType.open_port, severity=Severity.info,
                        title=f"Open port {p['port']}/{p['protocol']} ({p.get('service') or 'unknown'})",
                        port=p["port"], service=p.get("service"), raw_data=p,
                    )
                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.completed,
                                  finished_at=datetime.utcnow(), result_summary={"open_ports": len(result["ports"])})
            except Exception as e:
                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.failed,
                                  finished_at=datetime.utcnow(), error_message=str(e))
                raise
    _run_async(_do())


@celery_app.task(name="asm.run_tech_and_ssl_scan", bind=True)
def run_tech_and_ssl_scan(self, scan_id: str, asset_id: str, url: str, hostname: str):
    async def _do():
        async with AsyncSessionLocal() as db:
            await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.running, started_at=datetime.utcnow())
            try:
                tech = await detect_technologies(url)
                await _save_finding(
                    db, uuid.UUID(asset_id), uuid.UUID(scan_id),
                    finding_type=FindingType.technology, severity=Severity.info,
                    title=f"Detected stack: {', '.join(tech['technologies']) or 'none identified'}",
                    raw_data=tech,
                )

                ssl_result = await inspect_ssl(hostname)
                if ssl_result.get("reachable"):
                    if ssl_result.get("is_expired"):
                        sev, title = Severity.high, "TLS certificate has expired"
                    elif ssl_result.get("is_expiring_soon"):
                        sev, title = Severity.medium, f"TLS certificate expires in {ssl_result['days_remaining']} days"
                    elif ssl_result.get("weak_protocol"):
                        sev, title = Severity.high, f"Weak TLS protocol in use: {ssl_result['protocol']}"
                    else:
                        sev, title = Severity.info, "TLS configuration looks healthy"
                    await _save_finding(
                        db, uuid.UUID(asset_id), uuid.UUID(scan_id),
                        finding_type=FindingType.ssl_issue, severity=sev, title=title, raw_data=ssl_result,
                    )

                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.completed,
                                  finished_at=datetime.utcnow(), result_summary={"tech_count": len(tech["technologies"])})
            except Exception as e:
                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.failed,
                                  finished_at=datetime.utcnow(), error_message=str(e))
                raise
    _run_async(_do())


@celery_app.task(name="asm.run_vuln_scan", bind=True)
def run_vuln_scan_task(self, scan_id: str, asset_id: str, url: str):
    async def _do():
        async with AsyncSessionLocal() as db:
            await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.running, started_at=datetime.utcnow())
            try:
                findings = await run_vuln_scan(url)
                for f in findings:
                    await _save_finding(
                        db, uuid.UUID(asset_id), uuid.UUID(scan_id),
                        finding_type=FindingType.vulnerability, severity=Severity(f["severity"]),
                        title=f["title"], description=f.get("description"),
                        cve_id=f.get("cve_id"), raw_data=f["raw"],
                    )
                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.completed,
                                  finished_at=datetime.utcnow(),
                                  result_summary={"vulnerabilities_found": len(findings)})
            except Exception as e:
                await _mark_scan(db, uuid.UUID(scan_id), status=ScanStatus.failed,
                                  finished_at=datetime.utcnow(), error_message=str(e))
                raise
    _run_async(_do())
