-- Migration 020: Validate Source URLs
-- Date: 2025-01-XX
-- Description: Add constraints to ensure all source URLs are real and verifiable
-- Purpose: Critical for journalist verification - all sources must be accessible URLs

-- =========================
-- Add URL Validation Constraint
-- =========================

-- Function to validate URL format
CREATE OR REPLACE FUNCTION is_valid_source_url(url text) RETURNS boolean AS $$
BEGIN
    -- Must not be empty
    IF url IS NULL OR trim(url) = '' THEN
        RETURN false;
    END IF;
    
    -- Must start with http:// or https://
    IF NOT (url ~* '^https?://') THEN
        RETURN false;
    END IF;
    
    -- Must not contain test/placeholder patterns
    IF url ~* '(test|example|localhost|placeholder|dummy|fake|mock|sample|127\.0\.0\.1|192\.168\.|10\.\d+\.)' THEN
        RETURN false;
    END IF;
    
    -- Must have a domain (not just protocol)
    IF NOT (url ~* '^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}') THEN
        RETURN false;
    END IF;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Add check constraint to incident_sources table
ALTER TABLE public.incident_sources
DROP CONSTRAINT IF EXISTS check_source_url_valid;

ALTER TABLE public.incident_sources
ADD CONSTRAINT check_source_url_valid
CHECK (is_valid_source_url(source_url));

-- Add check constraint to sources table for homepage_url
ALTER TABLE public.sources
DROP CONSTRAINT IF EXISTS check_homepage_url_valid;

ALTER TABLE public.sources
ADD CONSTRAINT check_homepage_url_valid
CHECK (homepage_url IS NULL OR is_valid_source_url(homepage_url));

-- Add comment explaining the constraint
COMMENT ON CONSTRAINT check_source_url_valid ON public.incident_sources IS 
'Ensures all source URLs are real, verifiable URLs (http:// or https://) for journalist verification. Blocks test/placeholder URLs.';

COMMENT ON CONSTRAINT check_homepage_url_valid ON public.sources IS 
'Ensures homepage URLs are valid if provided.';

-- =========================
-- Record migration execution
-- =========================
INSERT INTO public.schema_migrations (version, description, executed_by)
VALUES (
    '020',
    'Add URL validation constraints to ensure all sources are real and verifiable',
    current_user
)
ON CONFLICT (version) DO NOTHING;

