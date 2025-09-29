from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from ..db import get_session
from ..schemas import IncidentIn, IncidentSourceIn
from ..utils.verification import normalize_domain, score_source, validate_article_fields
import os

router = APIRouter(prefix="/ingest", tags=["ingest"])

INGEST_TOKEN = os.getenv("INGEST_TOKEN")

def require_token(authorization: Optional[str] = Header(None)):
    if not INGEST_TOKEN:
        raise HTTPException(500, "Ingest token not configured")
    if not authorization or authorization != f"Bearer {INGEST_TOKEN}":
        raise HTTPException(401, "Unauthorized")

@router.post("", status_code=201)
async def ingest_incident(
    payload: IncidentIn,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    require_token(authorization)

    validate_article_fields(payload.title, payload.occurred_at, payload.lat, payload.lon)

    q = text("""
      select public.upsert_incident(
        :title, :narrative, :occurred_at, :lat, :lon, :asset_type, :status, :evidence_score, :country
      ) as id
    """)

    params = {
        "title": payload.title,
        "narrative": payload.narrative,
        "occurred_at": payload.occurred_at,
        "lat": payload.lat,
        "lon": payload.lon,
        "asset_type": payload.asset_type,
        "status": payload.status,
        "evidence_score": payload.evidence_score,
        "country": payload.country
    }

    rid = (await session.execute(q, params)).scalar_one()

    if payload.sources:
        for s in payload.sources:
            await _upsert_source_and_link(session, rid, s)

    await session.commit()
    return {"id": str(rid)}

async def _upsert_source_and_link(session: AsyncSession, incident_id, s: IncidentSourceIn):
    domain = normalize_domain(str(s.source_url)) or (s.domain or "")
    trust = s.trust_weight or score_source(domain, s.source_type)

    upsert_source_sql = text("""
      insert into public.sources(name,domain,source_type,homepage_url,trust_weight)
      values(:name,:domain,:type,null,:trust)
      on conflict (domain, source_type) do update set trust_weight=excluded.trust_weight
      returning id
    """)

    sid = (await session.execute(upsert_source_sql, {
        "name": s.source_name or domain or s.source_type,
        "domain": domain or None,
        "type": s.source_type,
        "trust": trust
    })).scalar_one()

    link_sql = text("""
      insert into public.incident_sources(incident_id, source_id, source_url, source_quote, lang)
      values(:iid,:sid,:url,:quote, null)
      on conflict do nothing
    """)

    await session.execute(link_sql, {
        "iid": incident_id,
        "sid": sid,
        "url": str(s.source_url),
        "quote": s.source_quote
    })