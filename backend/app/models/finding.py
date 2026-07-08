import uuid
import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Enum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FindingType(str, enum.Enum):
    open_port = "open_port"
    technology = "technology"
    ssl_issue = "ssl_issue"
    vulnerability = "vulnerability"
    misconfiguration = "misconfiguration"


class Severity(str, enum.Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id"), nullable=False)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id"), nullable=True)
    finding_type: Mapped[FindingType] = mapped_column(Enum(FindingType), nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.info)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    port: Mapped[int] = mapped_column(Integer, nullable=True)
    service: Mapped[str] = mapped_column(String(128), nullable=True)
    cve_id: Mapped[str] = mapped_column(String(64), nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_resolved: Mapped[bool] = mapped_column(default=False)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    asset: Mapped["Asset"] = relationship(back_populates="findings")
