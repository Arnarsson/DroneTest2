# Manual Database Cleanup

## Non-Incident to Remove

The following incident should be manually deleted from the database as it's regulatory news, not an actual incident:

### Incident Details
- **ID**: `61536178-b3db-47e6-9b58-69e5d48cfca9`
- **Title**: "Mange ministre kommer til byen - giver nyt droneforbud"
- **Type**: Regulatory news (drone ban announcement)
- **Reason**: This is about a temporary drone ban for an EU ministerial meeting, not an actual drone incident

### SQL Commands to Delete

```sql
-- Delete from Supabase SQL Editor
-- (Use direct connection port 5432, not pooler 6543)

-- 1. Delete related sources
DELETE FROM incident_sources
WHERE incident_id = '61536178-b3db-47e6-9b58-69e5d48cfca9';

-- 2. Delete the incident
DELETE FROM incidents
WHERE id = '61536178-b3db-47e6-9b58-69e5d48cfca9';
```

### Verification

After deletion, verify with:

```sql
-- Should return 0 rows
SELECT * FROM incidents
WHERE id = '61536178-b3db-47e6-9b58-69e5d48cfca9';
```

## Prevention

The `non_incident_filter.py` has been added to the ingestion pipeline to automatically filter out:
- Drone bans and restrictions
- Regulatory announcements
- Advisory notices
- Upcoming/planned restrictions

This will prevent similar non-incidents from being added in the future.
