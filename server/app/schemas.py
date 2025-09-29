from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID

EvidenceLevel = Literal[1,2,3,4]
Status = Literal["active","resolved","unconfirmed"]
AssetType = Literal["airport","harbor","military","other"]
SourceType = Literal["police","notam","media","social","other"]

class IncidentSourceIn(BaseModel):
    source_name: Optional[str] = None
    source_url: HttpUrl
    source_type: SourceType = "other"
    source_quote: Optional[str] = None
    domain: Optional[str] = None
    trust_weight: Optional[int] = None

class IncidentSourceOut(BaseModel):
    source_name: Optional[str] = None
    source_url: str
    source_type: str
    source_quote: Optional[str] = None
    domain: Optional[str] = None
    trust_weight: Optional[int] = None

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    narrative: Optional[str] = None
    occurred_at: datetime
    first_seen_at: datetime
    last_seen_at: datetime
    asset_type: Optional[AssetType] = None
    status: Status
    evidence_score: EvidenceLevel
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    sources: List[IncidentSourceOut] = []

class IncidentFilter(BaseModel):
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    min_evidence: Optional[int] = Field(default=1, ge=1, le=4)
    asset_type: Optional[AssetType] = None
    status: Optional[Status] = None
    country: Optional[str] = None
    bbox: Optional[List[float]] = None

class IncidentIn(BaseModel):
    title: str
    narrative: Optional[str] = None
    occurred_at: datetime
    lat: float
    lon: float
    asset_type: Optional[AssetType] = None
    status: Status = "active"
    evidence_score: EvidenceLevel = 1
    country: Optional[str] = None
    sources: Optional[List[IncidentSourceIn]] = []