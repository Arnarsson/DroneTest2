from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import logging
import asyncio
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add ingestion directory to path for deduplication modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ingestion'))

from db import run_async, get_connection
import asyncpg

# Import validation functions
try:
    from utils import is_drone_incident
except ImportError:
    # Fallback if utils not available
    logger.warning("utils module not available - drone validation disabled")
    is_drone_incident = None

# Import 3-tier duplicate detection system
try:
    from fuzzy_matcher import FuzzyMatcher
    from openrouter_deduplicator import OpenRouterEmbeddingDeduplicator
    from openrouter_llm_deduplicator import OpenRouterLLMDeduplicator
    DEDUP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Deduplication modules not available: {e}")
    DEDUP_AVAILABLE = False
    FuzzyMatcher = None
    OpenRouterEmbeddingDeduplicator = None
    OpenRouterLLMDeduplicator = None

logger = logging.getLogger(__name__)

def parse_datetime(dt_string):
    """Parse ISO datetime string to datetime object"""
    from datetime import timezone
    if not dt_string:
        return None
    if isinstance(dt_string, datetime):
        # Ensure timezone-aware
        if dt_string.tzinfo is None:
            return dt_string.replace(tzinfo=timezone.utc)
        return dt_string
    # Handle ISO format with 'Z' or timezone
    if dt_string.endswith('Z'):
        dt_string = dt_string[:-1] + '+00:00'
    dt = datetime.fromisoformat(dt_string)
    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

async def initialize_deduplicators(conn):
    """
    Initialize deduplicators for 3-tier duplicate detection.

    Args:
        conn: AsyncPG database connection

    Returns:
        (embedding_dedup, llm_dedup) tuple or (None, None) if not available
    """
    if not DEDUP_AVAILABLE:
        return None, None

    embedding_dedup = None
    llm_dedup = None

    # Initialize Tier 2: Embedding-based semantic detection
    try:
        embedding_dedup = OpenRouterEmbeddingDeduplicator(
            db_pool=conn,  # asyncpg Connection has same interface as Pool
            similarity_threshold=0.85
        )
        logger.info("Tier 2: OpenRouter embedding deduplicator initialized")
    except Exception as e:
        logger.warning(f"Tier 2: Failed to initialize embedding deduplicator: {e}")

    # Initialize Tier 3: LLM reasoning for edge cases
    try:
        llm_dedup = OpenRouterLLMDeduplicator(confidence_threshold=0.80)
        logger.info("Tier 3: LLM deduplicator initialized")
    except Exception as e:
        logger.warning(f"Tier 3: Failed to initialize LLM deduplicator: {e}")

    return embedding_dedup, llm_dedup

async def insert_incident(incident_data):
    """
    Insert incident or add as source to existing incident.

    Deduplication strategy:
    - Check for existing incident at same location (±1km)
    - If exists: Add as source, update evidence score, extend time range
    - If new: Create new incident
    - Result: One incident per location regardless of when events occurred
    """
    try:
        # Use shared database connection utility
        conn = await get_connection()

        # Parse datetime strings
        occurred_at = parse_datetime(incident_data.get('occurred_at'))
        first_seen_at = parse_datetime(incident_data.get('first_seen_at', incident_data.get('occurred_at')))
        last_seen_at = parse_datetime(incident_data.get('last_seen_at', incident_data.get('occurred_at')))

        lat = incident_data.get('lat')
        lon = incident_data.get('lon')
        title = incident_data.get('title', '')
        narrative = incident_data.get('narrative', '')
        asset_type = incident_data.get('asset_type', 'other')
        country = incident_data.get('country', 'DK')

        # ===== 3-TIER DUPLICATE DETECTION SYSTEM =====
        # Tier 1: Hash-based (FREE, <1ms, catches 70-80%)
        # Tier 2: Embeddings (FREE OpenRouter, 50-100ms, catches 15-20%)
        # Tier 3: LLM reasoning (FREE OpenRouter, 300-500ms, catches 5-10%)

        incident_id = None
        duplicate_tier = None
        duplicate_reason = None

        # Initialize deduplicators
        embedding_dedup, llm_dedup = await initialize_deduplicators(conn)

        # TIER 1: Source URL Check (existing logic - prevents race conditions)
        if incident_data.get('sources'):
            for source in incident_data['sources']:
                source_url = source.get('source_url', '')
                if source_url:
                    existing_incident = await conn.fetchrow("""
                        SELECT i.id, i.evidence_score, i.title, i.asset_type
                        FROM public.incidents i
                        JOIN public.incident_sources s ON i.id = s.incident_id
                        WHERE s.source_url = $1
                        LIMIT 1
                    """, source_url)
                    if existing_incident:
                        incident_id = existing_incident['id']
                        duplicate_tier = 1
                        duplicate_reason = "Source URL already exists"
                        logger.info(f"Tier 1: Found incident via source URL check: {existing_incident['title'][:50]}")
                        break

        # TIER 1.5: Fuzzy Title Matching (before creating incident)
        if incident_id is None and DEDUP_AVAILABLE and FuzzyMatcher:
            try:
                recent_incidents = await conn.fetch("""
                    SELECT id, title, occurred_at,
                           ST_Y(location::geometry) as lat,
                           ST_X(location::geometry) as lon
                    FROM public.incidents
                    WHERE ST_DWithin(
                        location::geography,
                        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                        5000  -- 5km radius
                    )
                    AND ABS(EXTRACT(EPOCH FROM (occurred_at - $3))) < 86400  -- 24 hours
                    LIMIT 10
                """, lon, lat, occurred_at)

                for candidate in recent_incidents:
                    similarity = FuzzyMatcher.similarity_ratio(title, candidate['title'])
                    if similarity >= 0.75:  # 75% fuzzy match threshold
                        incident_id = candidate['id']
                        duplicate_tier = 1
                        duplicate_reason = f"Fuzzy title match ({similarity:.1%})"
                        logger.info(
                            f"Tier 1: Fuzzy match found - similarity: {similarity:.1%}",
                            extra={
                                'new_title': title[:50],
                                'existing_title': candidate['title'][:50],
                                'incident_id': str(candidate['id'])
                            }
                        )
                        break
            except Exception as e:
                logger.warning(f"Tier 1: Fuzzy matching failed: {e}")

        # TIER 2: Embedding-Based Semantic Detection
        if incident_id is None and embedding_dedup:
            try:
                incident_dict = {
                    'title': title,
                    'location_name': incident_data.get('location_name', ''),
                    'lat': lat,
                    'lon': lon,
                    'asset_type': asset_type,
                    'occurred_at': occurred_at,
                    'narrative': narrative,
                    'country': country
                }

                duplicate_match = await embedding_dedup.find_duplicate(
                    incident=incident_dict,
                    time_window_hours=48,
                    distance_km=50
                )

                if duplicate_match:
                    dup_id, similarity, explanation = duplicate_match

                    # High confidence match (>0.92) - accept immediately
                    if similarity >= 0.92:
                        incident_id = dup_id
                        duplicate_tier = 2
                        duplicate_reason = f"Embedding similarity {similarity:.1%}: {explanation}"
                        logger.info(
                            f"Tier 2: High-confidence embedding match ({similarity:.1%})",
                            extra={
                                'incident_id': dup_id,
                                'explanation': explanation
                            }
                        )

                    # Borderline match (0.85-0.92) - escalate to Tier 3
                    elif llm_dedup:
                        logger.info(f"Tier 2: Borderline match ({similarity:.1%}), escalating to LLM")

                        # Fetch full candidate details for LLM analysis
                        candidate_full = await conn.fetchrow("""
                            SELECT
                                id, title, narrative, occurred_at, asset_type, country, evidence_score,
                                ST_Y(location::geometry) as lat,
                                ST_X(location::geometry) as lon
                            FROM public.incidents
                            WHERE id = $1
                        """, dup_id)

                        # TIER 3: LLM Reasoning for Edge Cases
                        try:
                            llm_result = await llm_dedup.analyze_potential_duplicate(
                                new_incident=incident_dict,
                                candidate=dict(candidate_full),
                                similarity_score=similarity
                            )

                            if llm_result:
                                is_duplicate, reasoning, confidence = llm_result

                                if is_duplicate and confidence >= 0.80:
                                    incident_id = dup_id
                                    duplicate_tier = 3
                                    duplicate_reason = f"LLM confirmed ({confidence:.1%}): {reasoning}"
                                    logger.info(
                                        f"Tier 3: LLM confirmed duplicate (confidence: {confidence:.1%})",
                                        extra={
                                            'incident_id': dup_id,
                                            'reasoning': reasoning
                                        }
                                    )
                                else:
                                    logger.info(
                                        f"Tier 3: LLM classified as unique (confidence: {confidence:.1%})",
                                        extra={'reasoning': reasoning}
                                    )
                            else:
                                # LLM unavailable (rate limited) - skip Tier 3
                                logger.info("Tier 3: LLM unavailable, treating borderline match as unique")
                        except Exception as e:
                            logger.warning(f"Tier 3: LLM analysis failed: {e}")

            except Exception as e:
                logger.error(f"Tier 2/3: Error during duplicate detection: {e}", exc_info=True)

        # TIER 2 FALLBACK: Geographic Consolidation (existing logic as final fallback)
        # If no duplicate found via source URL, fuzzy matching, or semantic detection,
        # fall back to geographic radius matching (original implementation)
        if incident_id is None:
            search_radius = {
                'airport': 3000,    # 3km - airports are large
                'military': 3000,   # 3km - military bases are large
                'harbor': 1500,     # 1.5km - harbors are medium
                'powerplant': 1000, # 1km - power plants
                'bridge': 500,      # 500m - bridges are specific
                'other': 500        # 500m - default for unknown
            }.get(asset_type, 500)

            # Check for existing incident within radius AND within 7 days
            # This prevents merging incidents that are weeks/months apart
            existing_incident = await conn.fetchrow("""
                SELECT id, evidence_score, title, asset_type, occurred_at
                FROM public.incidents
                WHERE ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                    $3  -- Dynamic radius based on asset type
                )
                AND asset_type = $4  -- Must be same asset type
                AND occurred_at >= $5 - INTERVAL '7 days'  -- Within 7 days
                AND occurred_at <= $5 + INTERVAL '7 days'   -- Within 7 days
                ORDER BY occurred_at ASC
                LIMIT 1
            """, lon, lat, search_radius, asset_type, occurred_at)

            if existing_incident:
                incident_id = existing_incident['id']
                duplicate_tier = 0  # Fallback tier
                duplicate_reason = f"Geographic consolidation ({search_radius}m radius)"
                logger.info(f"Fallback: Geographic consolidation matched: {existing_incident['title'][:50]}")

        existing_incident = None
        if incident_id:
            # Re-fetch incident details for consistency
            existing_incident = await conn.fetchrow("""
                SELECT id, evidence_score, title, asset_type
                FROM public.incidents
                WHERE id = $1
            """, incident_id)

        if existing_incident:
            # Incident already exists - add this as a source instead
            incident_id = existing_incident['id']
            logger.info(f"Found existing incident: {existing_incident['title'][:50]}")
            logger.info(f"Adding new article as source: {incident_data['title'][:50]}")

            # Log which tier caught the duplicate
            if duplicate_tier is not None:
                tier_names = {
                    0: "Geographic fallback",
                    1: "Hash/Fuzzy",
                    2: "Embedding",
                    3: "LLM"
                }
                logger.info(
                    f"Duplicate detection metrics",
                    extra={
                        'tier': duplicate_tier,
                        'tier_name': tier_names.get(duplicate_tier, 'Unknown'),
                        'reason': duplicate_reason,
                        'incident_id': str(incident_id)
                    }
                )

            # Update time range to encompass all events at this location
            await conn.execute("""
                UPDATE public.incidents
                SET
                    first_seen_at = LEAST(first_seen_at, $1),
                    last_seen_at = GREATEST(last_seen_at, $2),
                    occurred_at = LEAST(occurred_at, $3)
                WHERE id = $4
            """, first_seen_at, last_seen_at, occurred_at, incident_id)

        else:
            # New incident - create it
            query = """
            INSERT INTO public.incidents
            (title, narrative, occurred_at, first_seen_at, last_seen_at,
             asset_type, status, evidence_score, country, location, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9,
                    ST_SetSRID(ST_MakePoint($10, $11), 4326), $12)
            RETURNING id
            """

            incident_id = await conn.fetchval(
                query,
                incident_data['title'],
                incident_data.get('narrative', ''),
                occurred_at,
                first_seen_at,
                last_seen_at,
                incident_data.get('asset_type', 'other'),
                incident_data.get('status', 'active'),
                incident_data.get('evidence_score', 1),
                incident_data.get('country', 'DK'),
                incident_data.get('lon'),
                incident_data.get('lat'),
                incident_data.get('verification_status', 'pending')
            )

            # TIER 2: Generate and store embedding for future similarity searches
            if embedding_dedup:
                try:
                    incident_dict = {
                        'title': title,
                        'location_name': incident_data.get('location_name', ''),
                        'lat': lat,
                        'lon': lon,
                        'asset_type': asset_type,
                        'occurred_at': occurred_at,
                        'narrative': narrative,
                        'country': country
                    }
                    embedding = await embedding_dedup.generate_embedding(incident_dict)
                    await embedding_dedup.store_embedding(str(incident_id), embedding)
                    logger.info(f"Tier 2: Embedding stored for new incident {incident_id}")
                except Exception as e:
                    logger.warning(f"Tier 2: Failed to store embedding for {incident_id}: {e}")

            logger.info(f"Created new incident: {incident_data['title'][:50]}")

        # Insert sources if provided
        # NOTE: After sources are inserted, the database trigger 'trigger_update_evidence_score'
        # will automatically recalculate the incident's evidence_score based on source trust_weights
        if incident_data.get('sources'):
            for source in incident_data['sources']:
                try:
                    # Extract domain from source_url (already validated above)
                    from urllib.parse import urlparse
                    source_url = source.get('source_url', '').strip()
                    if not source_url:
                        logger.warning("Skipping source with empty URL")
                        continue
                    
                    parsed = urlparse(source_url)
                    domain = parsed.netloc or 'unknown'
                    
                    # Ensure domain is valid (not 'unknown' or empty)
                    if domain == 'unknown' or not domain:
                        logger.error(f"Invalid source URL domain: {source_url}")
                        continue

                    # First, get or create source in sources table
                    # Schema: UNIQUE (domain, source_type) - see sql/supabase_schema_v2.sql line 45
                    source_id = await conn.fetchval("""
                        INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (domain, source_type)
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            trust_weight = GREATEST(sources.trust_weight, EXCLUDED.trust_weight)
                        RETURNING id
                    """,
                        source.get('source_name', 'Unknown'),  # name field
                        domain,  # domain field
                        source.get('source_type', 'other'),  # source_type (required)
                        source.get('source_url', ''),  # homepage_url (use source_url)
                        source.get('trust_weight', 1)  # trust_weight
                    )

                    # Then insert into incident_sources junction table
                    # This INSERT triggers automatic evidence_score recalculation
                    await conn.execute("""
                        INSERT INTO public.incident_sources
                        (incident_id, source_id, source_url, source_title, source_quote)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (incident_id, source_url) DO NOTHING
                    """,
                        incident_id,
                        source_id,
                        source.get('source_url', ''),
                        source.get('source_name', ''),  # source_title
                        source.get('source_quote', '')
                    )
                except Exception as source_error:
                    # Log source insertion errors but continue with incident
                    logger.error(f"Failed to insert source: {source_error}")
                    continue

        # Close connection gracefully (with timeout for serverless)
        try:
            await asyncio.wait_for(conn.close(), timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Connection close timed out (normal for serverless)")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

        return {"id": str(incident_id), "status": "created"}

    except Exception as e:
        import traceback
        # SECURITY: Log full traceback server-side only, never expose to client
        # Exposing tracebacks reveals internal file paths, database schema,
        # and implementation details that can aid attackers
        traceback.print_exc()  # Server-side logging for debugging
        logger.error(f"Database error: {type(e).__name__}: {str(e)}")

        # Return generic error to client - no internal details
        return {
            "error": "Internal server error",
            "detail": "Failed to process incident. Check server logs for details."
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Check authorization with security best practices
        import secrets
        expected_token = os.getenv('INGEST_TOKEN')
        if not expected_token:
            error_msg = (
                "Server configuration error: INGEST_TOKEN not set. "
                "Set it in Vercel: Settings → Environment Variables"
            )
            logger.error(error_msg)
            self.send_error(500, error_msg)
            return
        
        # Validate token format (minimum security requirement)
        if len(expected_token) < 16:
            error_msg = (
                "Server configuration error: INGEST_TOKEN too short. "
                "Minimum 16 characters required for security."
            )
            logger.error(error_msg)
            self.send_error(500, error_msg)
            return

        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_error(401, "Missing Bearer token")
            return

        token = auth_header.replace('Bearer ', '')
        # Use constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(token, expected_token):
            self.send_error(403, "Invalid token")
            return

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "Empty request body")
            return

        body = self.rfile.read(content_length)

        try:
            incident_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        # Validate required fields
        required_fields = ['title', 'occurred_at', 'lat', 'lon']
        missing = [f for f in required_fields if f not in incident_data]
        if missing:
            self.send_error(400, f"Missing required fields: {', '.join(missing)}")
            return

        # Validate and sanitize title field (CRITICAL for XSS prevention)
        from text_validation import validate_title, validate_narrative

        title_valid, sanitized_title, title_error = validate_title(incident_data.get('title'))
        if not title_valid:
            logger.error(f"Title validation failed: {title_error}")
            self.send_error(400, f"Title validation failed: {title_error}")
            return

        # Validate and sanitize narrative field if present
        narrative_valid, sanitized_narrative, narrative_error = validate_narrative(
            incident_data.get('narrative')
        )
        if not narrative_valid:
            logger.error(f"Narrative validation failed: {narrative_error}")
            self.send_error(400, f"Narrative validation failed: {narrative_error}")
            return

        # Apply sanitized values
        incident_data['title'] = sanitized_title
        incident_data['narrative'] = sanitized_narrative

        # === CRITICAL: Validate this is actually a drone incident ===
        title = sanitized_title
        narrative = sanitized_narrative
        full_text = (title + " " + narrative).lower()

        # Exclude non-drone incidents (avalanches, deaths, accidents, etc.)
        non_drone_keywords = [
            "avalanche", "lavine", "lawine",  # Avalanche
            "killed", "died", "death", "død", "dödsfall", "kuolema",  # Deaths
            "fatal", "fatality", "dødsulykke",  # Fatalities
            "accident", "ulykke", "onnettomuus",  # Accidents (not drone-related)
            "earthquake", "jordskælv", "jordskjelv",  # Natural disasters
            "flood", "oversvømmelse", "flod",  # Floods
            "fire", "brand", "tulipalo",  # Fires (unless drone-related)
            "terror", "terrorist", "terrorisme",  # Terrorism
            "shooting", "skud", "ammuskelu",  # Shootings
            "bomb", "bombe", "pommi",  # Bombs
            "war", "krig", "sota",  # War
        ]

        # Check if it contains non-drone incident keywords
        if any(keyword in full_text for keyword in non_drone_keywords):
            # Only exclude if it doesn't also mention drones
            if "drone" not in full_text and "dron" not in full_text and "drohne" not in full_text:
                logger.warning(f"🚫 BLOCKED (Non-drone incident): {title[:60]}")
                self.send_error(400, "This incident is not drone-related. Only drone incidents are accepted.")
                return

        # Validate it's actually a drone incident using the same logic as ingestion pipeline
        if is_drone_incident:
            if not is_drone_incident(title, narrative):
                logger.warning(f"🚫 BLOCKED (Not a drone incident): {title[:60]}")
                self.send_error(400, "This incident does not appear to be drone-related. Only verified drone incidents are accepted.")
                return

        # Validate source URLs are real and verifiable (CRITICAL for journalists)
        if incident_data.get('sources'):
            from source_validation import validate_all_sources
            
            all_valid, validation_errors = validate_all_sources(incident_data['sources'])
            
            if not all_valid:
                error_msg = (
                    "Invalid source URLs detected. All sources must be real, verifiable URLs "
                    "for journalist verification:\n" +
                    "\n".join(f"  - {msg}" for msg in validation_errors)
                )
                logger.error(f"Source validation failed: {error_msg}")
                self.send_error(400, error_msg)
                return

        # Insert into database
        result = run_async(insert_incident(incident_data))

        # Handle CORS - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronemap.cc',
            'https://www.dronewatch.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')

        if 'error' in result:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
        else:
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Location', f'/api/incidents/{result["id"]}')

        # Only allow whitelisted origins
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        elif origin:
            # Origin provided but not allowed - reject
            logger.warning(f"Blocked CORS request from unauthorized origin: {origin}")

        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight - whitelist specific origins only
        ALLOWED_ORIGINS = [
            'https://www.dronemap.cc',
            'https://dronemap.cc',
            'https://www.dronewatch.cc',
            'https://dronewatch.cc',
            'http://localhost:3000',
            'http://localhost:3001'
        ]

        origin = self.headers.get('Origin', '')
        self.send_response(200)

        # Only allow whitelisted origins
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        elif origin:
            # Origin provided but not allowed - reject with 403
            logger.warning(f"Blocked CORS preflight from unauthorized origin: {origin}")
            self.send_response(403)

        self.end_headers()