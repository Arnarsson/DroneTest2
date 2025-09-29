-- Enable PostGIS (run once in your Supabase project)
create extension if not exists postgis;

-- =========================
-- Core reference: assets (airports/harbors/military)
-- =========================
create table if not exists public.assets (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type text not null check (type in ('airport','harbor','military','other')),
  location geography(Point, 4326) not null,
  icao text,
  iata text,
  country text,
  created_at timestamptz not null default now()
);

create index if not exists idx_assets_gix on public.assets using gist (location);
create index if not exists idx_assets_type on public.assets(type);

-- =========================
-- Sources (canonical publisher domains/accounts)
-- =========================
create table if not exists public.sources (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  domain text,                 -- e.g., politi.dk, reuters.com
  source_type text not null check (source_type in ('police','notam','media','social','other')),
  homepage_url text,
  trust_weight int not null default 1,  -- 1..4 (aligns with evidence scoring)
  created_at timestamptz not null default now(),
  unique (domain, source_type)
);

-- =========================
-- Incidents
-- =========================
create table if not exists public.incidents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  narrative text,
  occurred_at timestamptz not null,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  location geography(Point, 4326) not null,
  asset_type text check (asset_type in ('airport','harbor','military','other')),
  status text not null default 'active' check (status in ('active','resolved','unconfirmed')),
  evidence_score int not null default 1 check (evidence_score between 1 and 4),
  country text,
  admin_notes text
);

create index if not exists idx_incidents_gix on public.incidents using gist (location);
create index if not exists idx_incidents_time on public.incidents(occurred_at);
create index if not exists idx_incidents_evidence on public.incidents(evidence_score);
create index if not exists idx_incidents_status on public.incidents(status);

-- =========================
-- Incident <-> Sources (many-to-many)
-- =========================
create table if not exists public.incident_sources (
  incident_id uuid references public.incidents(id) on delete cascade,
  source_id uuid references public.sources(id) on delete cascade,
  source_url text not null,
  source_quote text,  -- exact quote extracted for verification
  lang text,
  primary key (incident_id, source_id, source_url)
);

-- =========================
-- Public read access via RLS (anon can SELECT only)
-- =========================
alter table public.incidents enable row level security;
alter table public.sources enable row level security;
alter table public.assets enable row level security;
alter table public.incident_sources enable row level security;

-- Policies: allow read to anon, block writes
create policy "anon_read_incidents" on public.incidents
  for select using (true);
create policy "anon_read_sources" on public.sources
  for select using (true);
create policy "anon_read_assets" on public.assets
  for select using (true);
create policy "anon_read_incident_sources" on public.incident_sources
  for select using (true);

-- (Writes should be via service role only; don't create insert/update policies for anon.)

-- =========================
-- Helper: upsert function (optional)
-- =========================
create or replace function public.upsert_incident(
  p_title text,
  p_narrative text,
  p_occurred_at timestamptz,
  p_lat double precision,
  p_lng double precision,
  p_asset_type text,
  p_status text,
  p_evidence_score int,
  p_country text
) returns uuid
language plpgsql as $$
declare
  v_id uuid;
begin
  -- naive dedupe by title+occurred_at (tune as you wish)
  select id into v_id from public.incidents
   where title = p_title and occurred_at = p_occurred_at
   limit 1;

  if v_id is null then
    insert into public.incidents(title,narrative,occurred_at,location,asset_type,status,evidence_score,country)
    values(
      p_title, p_narrative, p_occurred_at,
      ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography,
      p_asset_type, p_status, p_evidence_score, p_country
    )
    returning id into v_id;
  else
    update public.incidents
      set narrative = coalesce(p_narrative, narrative),
          asset_type = coalesce(p_asset_type, asset_type),
          status = coalesce(p_status, status),
          evidence_score = greatest(evidence_score, p_evidence_score),
          last_seen_at = now()
    where id = v_id;
  end if;

  return v_id;
end$$;