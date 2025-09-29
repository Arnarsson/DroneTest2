from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from ..db import get_session
from ..schemas import IncidentOut

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("", response_model=List[IncidentOut])
async def list_incidents(
    since: Optional[str] = Query(None, description="ISO datetime"),
    until: Optional[str] = Query(None, description="ISO datetime"),
    min_evidence: int = Query(1, ge=1, le=4),
    asset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    bbox: Optional[str] = Query(None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(200, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    base = """
    select i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
           i.asset_type, i.status, i.evidence_score, i.country,
           ST_Y(i.location::geometry) as lat,
           ST_X(i.location::geometry) as lon
    from public.incidents i
    where i.evidence_score >= :min_evidence
    """
    params = {"min_evidence": min_evidence}

    if since:
        base += " and i.occurred_at >= :since"
        params["since"] = since
    if until:
        base += " and i.occurred_at <= :until"
        params["until"] = until
    if asset_type:
        base += " and i.asset_type = :asset_type"
        params["asset_type"] = asset_type
    if status:
        base += " and i.status = :status"
        params["status"] = status
    if country:
        base += " and i.country = :country"
        params["country"] = country
    if bbox:
        try:
            minLon, minLat, maxLon, maxLat = [float(x) for x in bbox.split(",")]
            base += " and ST_Within(i.location::geometry, ST_MakeEnvelope(:minLon,:minLat,:maxLon,:maxLat,4326))"
            params.update({"minLon": minLon, "minLat": minLat, "maxLon": maxLon, "maxLat": maxLat})
        except Exception:
            raise HTTPException(400, "Invalid bbox format")

    base += " order by i.occurred_at desc limit :limit"
    params["limit"] = limit

    rows = (await session.execute(text(base), params)).mappings().all()

    out = []
    for r in rows:
        r = dict(r)
        r["sources"] = []
        out.append(r)
    return out

@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: str, session: AsyncSession = Depends(get_session)):
    q = """
    select i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
           i.asset_type, i.status, i.evidence_score, i.country,
           ST_Y(i.location::geometry) as lat,
           ST_X(i.location::geometry) as lon
    from public.incidents i
    where i.id = :id
    limit 1
    """
    rec = (await session.execute(text(q), {"id": incident_id})).mappings().first()
    if not rec:
        raise HTTPException(404, "Incident not found")

    s = """
    select s.name as source_name, s.domain, s.source_type, s.trust_weight,
           isrc.source_url, isrc.source_quote
    from public.incident_sources isrc
    join public.sources s on s.id = isrc.source_id
    where isrc.incident_id = :id
    """
    srcs = (await session.execute(text(s), {"id": incident_id})).mappings().all()
    rec = dict(rec)
    rec["sources"] = [dict(x) for x in srcs]
    return rec