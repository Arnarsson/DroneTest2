-- Demo data for testing
insert into public.assets(name,type,location,icao,country)
values
('Copenhagen Airport','airport', ST_SetSRID(ST_MakePoint(12.6476,55.6180),4326)::geography,'EKCH','DK'),
('Aalborg Airport','airport', ST_SetSRID(ST_MakePoint(9.8492,57.0928),4326)::geography,'EKYT','DK');

insert into public.sources(name,domain,source_type,homepage_url,trust_weight)
values
('Nordjyllands Politi','politi.dk','police','https://politi.dk',4),
('NOTAM (FAA portal)','notams.aim.faa.gov','notam','https://notams.aim.faa.gov',4),
('Reuters','reuters.com','media','https://www.reuters.com',3);

-- Example incident (Aalborg)
select public.upsert_incident(
  'Drones observed over Aalborg Airport',
  'Police reported multiple drones over airport; operations impacted.',
  now() - interval '2 hours',
  57.0928, 9.8492,
  'airport','active',4,'DK'
) as incident_id \gset

insert into public.incident_sources(incident_id, source_id, source_url, source_quote, lang)
select :'incident_id', s.id, 'https://politi.dk/nordjyllands-politi/nyhed/droner-over-aalborg-lufthavn/548681','Der er lørdag aften kl. 21:44 indgivet anmeldelse...', 'da'
from public.sources s where s.domain='politi.dk';