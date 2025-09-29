"""
DroneWatch API - Vercel Serverless Function
Main entry point for all API routes
"""
from fastapi import FastAPI, Response, Query, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID
import os
import json

# Initialize FastAPI
app = FastAPI(
    title="DroneWatch API",
    version="0.1.0",
    description="Verified drone incident tracking API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://dronewatch.cc,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# SCHEMAS
# ======================

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

class IncidentIn(BaseModel):
    title: str
    narrative: Optional[str] = None
    occurred_at: datetime
    lat: float
    lon: float
    location_name: Optional[str] = None
    asset_type: Optional[AssetType] = None
    status: Status = "active"
    evidence_score: EvidenceLevel = 1
    country: Optional[str] = None
    content_hash: Optional[str] = None
    sources: Optional[List[IncidentSourceIn]] = []

# ======================
# DATABASE
# ======================

async def get_db_connection():
    """Get async database connection"""
    import asyncpg

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # Convert from Supabase format if needed
        SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
        if "supabase.co" in SUPABASE_URL:
            project_ref = SUPABASE_URL.split("//")[1].split(".")[0]
            DATABASE_URL = f"postgresql://postgres.{project_ref}:{SUPABASE_SERVICE_KEY}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    return await asyncpg.connect(DATABASE_URL)

# ======================
# ENDPOINTS
# ======================

@app.get("/api")
async def root():
    """Root endpoint"""
    return {
        "name": "DroneWatch API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "status": "operational"
    }

@app.get("/api/healthz")
async def health():
    """Health check"""
    try:
        conn = await get_db_connection()
        await conn.fetchval("SELECT 1")
        await conn.close()
        return {"ok": True, "service": "dronewatch-api"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/incidents", response_model=List[IncidentOut])
async def list_incidents(
    response: Response,
    since: Optional[str] = Query(None, description="ISO datetime"),
    until: Optional[str] = Query(None, description="ISO datetime"),
    min_evidence: int = Query(1, ge=1, le=4),
    asset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    bbox: Optional[str] = Query(None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List incidents with filters"""
    conn = await get_db_connection()

    try:
        # Build query
        query = """
        SELECT i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
               i.asset_type, i.status, i.evidence_score, i.country,
               ST_Y(i.location::geometry) as lat,
               ST_X(i.location::geometry) as lon
        FROM public.incidents i
        WHERE i.evidence_score >= $1
        """
        params = [min_evidence]
        param_count = 1

        if since:
            param_count += 1
            query += f" AND i.occurred_at >= ${param_count}"
            params.append(since)

        if until:
            param_count += 1
            query += f" AND i.occurred_at <= ${param_count}"
            params.append(until)

        if asset_type:
            param_count += 1
            query += f" AND i.asset_type = ${param_count}"
            params.append(asset_type)

        if status:
            param_count += 1
            query += f" AND i.status = ${param_count}"
            params.append(status)

        if country:
            param_count += 1
            query += f" AND i.country = ${param_count}"
            params.append(country)

        if bbox:
            try:
                minLon, minLat, maxLon, maxLat = [float(x) for x in bbox.split(",")]
                if not (-180 <= minLon <= 180 and -180 <= maxLon <= 180 and
                        -90 <= minLat <= 90 and -90 <= maxLat <= 90):
                    raise HTTPException(400, "BBox coordinates out of range")
                if minLon >= maxLon or minLat >= maxLat:
                    raise HTTPException(400, "Invalid bbox: min values must be less than max")

                param_count += 4
                query += f" AND ST_Within(i.location::geometry, ST_MakeEnvelope(${param_count-3},${param_count-2},${param_count-1},${param_count},4326))"
                params.extend([minLon, minLat, maxLon, maxLat])
            except ValueError:
                raise HTTPException(400, "Invalid bbox format")

        query += f" ORDER BY i.occurred_at DESC LIMIT ${param_count+1} OFFSET ${param_count+2}"
        params.extend([limit, offset])

        # Execute query
        rows = await conn.fetch(query, *params)

        # Format results
        incidents = []
        for row in rows:
            incidents.append({
                "id": row["id"],
                "title": row["title"],
                "narrative": row["narrative"],
                "occurred_at": row["occurred_at"],
                "first_seen_at": row["first_seen_at"],
                "last_seen_at": row["last_seen_at"],
                "asset_type": row["asset_type"],
                "status": row["status"],
                "evidence_score": row["evidence_score"],
                "country": row["country"],
                "lat": row["lat"],
                "lon": row["lon"],
                "sources": []
            })

        # Add cache header
        response.headers["Cache-Control"] = "public, max-age=15"

        return incidents

    finally:
        await conn.close()

@app.get("/api/incidents/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: str):
    """Get incident by ID"""
    conn = await get_db_connection()

    try:
        # Get incident
        query = """
        SELECT i.id, i.title, i.narrative, i.occurred_at, i.first_seen_at, i.last_seen_at,
               i.asset_type, i.status, i.evidence_score, i.country,
               ST_Y(i.location::geometry) as lat,
               ST_X(i.location::geometry) as lon
        FROM public.incidents i
        WHERE i.id = $1
        """
        row = await conn.fetchrow(query, incident_id)

        if not row:
            raise HTTPException(404, "Incident not found")

        # Get sources
        sources_query = """
        SELECT s.name as source_name, s.domain, s.source_type, s.trust_weight,
               isrc.source_url, isrc.source_quote
        FROM public.incident_sources isrc
        JOIN public.sources s ON s.id = isrc.source_id
        WHERE isrc.incident_id = $1
        """
        sources = await conn.fetch(sources_query, incident_id)

        return {
            "id": row["id"],
            "title": row["title"],
            "narrative": row["narrative"],
            "occurred_at": row["occurred_at"],
            "first_seen_at": row["first_seen_at"],
            "last_seen_at": row["last_seen_at"],
            "asset_type": row["asset_type"],
            "status": row["status"],
            "evidence_score": row["evidence_score"],
            "country": row["country"],
            "lat": row["lat"],
            "lon": row["lon"],
            "sources": [dict(s) for s in sources]
        }

    finally:
        await conn.close()

@app.post("/api/ingest", status_code=201)
async def ingest_incident(
    payload: IncidentIn,
    authorization: Optional[str] = Header(None)
):
    """Ingest new incident (protected)"""
    # Check auth
    INGEST_TOKEN = os.getenv("INGEST_TOKEN")
    if not INGEST_TOKEN:
        raise HTTPException(500, "Ingest token not configured")
    if not authorization or authorization != f"Bearer {INGEST_TOKEN}":
        raise HTTPException(401, "Unauthorized")

    # Validate
    if not payload.title or not payload.occurred_at:
        raise HTTPException(400, "Missing required fields")
    if not (-90 <= payload.lat <= 90 and -180 <= payload.lon <= 180):
        raise HTTPException(400, "Invalid coordinates")

    conn = await get_db_connection()

    try:
        # Call upsert function
        query = """
        SELECT public.upsert_incident_v2(
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
        ) as id
        """

        incident_id = await conn.fetchval(
            query,
            payload.title,
            payload.narrative,
            payload.occurred_at,
            payload.lat,
            payload.lon,
            payload.location_name,
            payload.asset_type,
            payload.status,
            payload.evidence_score,
            payload.country,
            payload.content_hash,
            json.dumps([]),  # quotes
            json.dumps([])   # confirmations
        )

        # Add sources if provided
        if payload.sources:
            for source in payload.sources:
                # Upsert source
                source_query = """
                INSERT INTO public.sources(name, domain, source_type, homepage_url, trust_weight)
                VALUES($1, $2, $3, $4, $5)
                ON CONFLICT (domain, source_type, homepage_url)
                DO UPDATE SET trust_weight = EXCLUDED.trust_weight
                RETURNING id
                """

                source_id = await conn.fetchval(
                    source_query,
                    source.source_name or source.domain,
                    source.domain,
                    source.source_type,
                    str(source.source_url),
                    source.trust_weight or 2
                )

                # Link to incident
                link_query = """
                INSERT INTO public.incident_sources(incident_id, source_id, source_url, source_quote)
                VALUES($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                """

                await conn.execute(
                    link_query,
                    incident_id,
                    source_id,
                    str(source.source_url),
                    source.source_quote
                )

        return {"id": str(incident_id)}

    finally:
        await conn.close()

@app.get("/api/embed/snippet", response_class=HTMLResponse)
def embed_snippet(
    min_evidence: int = Query(2, ge=1, le=4),
    country: str | None = Query(None),
    height: int = Query(500, ge=300, le=2000)
):
    """Get embed iframe snippet"""
    params = f"minEvidence={min_evidence}"
    if country:
        params += f"&country={country}"

    html = f"""
    <!-- DroneWatch Embed -->
    <iframe
      src="https://dronewatch.cc/embed/map?{params}"
      width="100%"
      height="{height}"
      style="border:0;overflow:hidden"
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"
      ></iframe>
    """
    return HTMLResponse(content=html.strip())

# Export handler for Vercel
handler = app