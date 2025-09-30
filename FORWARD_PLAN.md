# DroneWatch Forward Plan

## Current Status ✅
- **Frontend**: Live at https://www.dronemap.cc
- **API**: Working with 29 incidents (will be 16 after deduplication)
- **Database**: Supabase with PostgreSQL + PostGIS
- **Scraper**: GitHub Actions running every 15 minutes
- **Historical Data**: September 2025 European drone incidents loaded

---

## Phase 1: Data Quality & Cleanup (Immediate - This Week)

### 1.1 Deduplication System
- [x] Manual cleanup of current duplicates (SQL script provided)
- [ ] **Add unique constraint** on (lat, lon, occurred_at) to prevent future duplicates
- [ ] **Implement hash-based detection** in scraper to check before inserting
- [ ] Create `processed_incidents.json` in scraper to track seen incidents

### 1.2 Data Enrichment
- [ ] **Add missing Copenhagen Airport main incident** (4-hour closure on Sept 22)
- [ ] **Verify all incident locations** have correct coordinates
- [ ] **Add source citations** where missing (police reports, NOTAM, news)
- [ ] **Standardize narrative format**: Start with facts, then context, then impact

### 1.3 Evidence Scoring
Current system: 1-4 scale
- [ ] **Document evidence criteria** clearly in README
- [ ] **Audit existing scores** - ensure consistency
- [ ] Consider: Should we require sources for scores 3-4?

---

## Phase 2: Scraper Enhancement (Next 1-2 Weeks)

### 2.1 Source Expansion
**Current**: Danish police RSS + Google News Denmark
**Add**:
- [ ] **Norwegian sources**: politiet.no, avinor.no
- [ ] **Swedish sources**: polisen.se, lfv.se (Swedish ATC)
- [ ] **Polish sources**: policja.pl, pansa.pl
- [ ] **NOTAM feeds**: eurocontrol.int aviation notices
- [ ] **FlightRadar24 incidents** (if API available)

### 2.2 Scraper Intelligence
- [ ] **NLP for classification**: Auto-detect airport vs military vs harbor
- [ ] **Geocoding**: Auto-extract locations from text (spaCy or similar)
- [ ] **Duplicate detection**: Check similarity before inserting
- [ ] **Confidence scoring**: Rate scraper's confidence in data quality

### 2.3 Alert System
- [ ] **Webhook notifications** when new incidents appear
- [ ] **Email digest**: Daily summary of new incidents
- [ ] **Severity levels**: Critical (airport closure) vs Minor (sighting)

---

## Phase 3: Frontend Features (Next 2-4 Weeks)

### 3.1 Map Improvements
- [ ] **Incident clustering**: Better visualization when zoomed out
- [ ] **Timeline slider**: Show incidents over time
- [ ] **Heat map mode**: Show incident density by region
- [ ] **Animation**: Replay incidents chronologically

### 3.2 Incident Details
- [ ] **Source links**: Display all sources for each incident
- [ ] **Related incidents**: Show nearby incidents in same timeframe
- [ ] **Media gallery**: Add photos/videos when available
- [ ] **Export**: Download incidents as CSV/JSON

### 3.3 Analytics Dashboard
- [ ] **Statistics**: Total incidents, by country, by type
- [ ] **Trends**: Incidents per day/week/month graph
- [ ] **Top locations**: Most frequently affected airports
- [ ] **Evidence breakdown**: Pie chart of evidence levels

### 3.4 User Features
- [ ] **Report incident**: User submission form (with moderation)
- [ ] **Subscribe**: Email notifications for specific countries/regions
- [ ] **Embed widget**: Iframe-able map for news sites

---

## Phase 4: Data Analysis & Insights (Ongoing)

### 4.1 Pattern Detection
- [ ] **Coordinated attacks**: Flag incidents happening simultaneously
- [ ] **Recurring locations**: Identify frequently targeted sites
- [ ] **Time patterns**: Peak hours/days for incidents
- [ ] **Geopolitical correlation**: Map to regional tensions

### 4.2 Export & Sharing
- [ ] **Public API**: REST API for researchers
- [ ] **Dataset releases**: Monthly CSV dumps on GitHub
- [ ] **Academic partnerships**: Share data with universities
- [ ] **OSINT community**: Connect with Bellingcat, ACLED, etc.

---

## Phase 5: Infrastructure & Scale (1-2 Months)

### 5.1 Performance
- [ ] **CDN caching**: CloudFlare for static assets
- [ ] **API caching**: Redis for frequently accessed data
- [ ] **Database optimization**: Add indexes on common queries
- [ ] **Pagination**: Implement proper API pagination

### 5.2 Monitoring
- [ ] **Error tracking**: Sentry or similar for API errors
- [ ] **Uptime monitoring**: Pingdom or UptimeRobot
- [ ] **Analytics**: Plausible or PostHog for usage stats
- [ ] **Scraper health**: Alert if scraper fails

### 5.3 Deployment
- [ ] **CI/CD pipeline**: Automated testing + deployment
- [ ] **Staging environment**: Test changes before production
- [ ] **Database backups**: Automated daily backups
- [ ] **Rollback plan**: Easy revert if issues occur

---

## Phase 6: Community & Growth (2-3 Months)

### 6.1 Content
- [ ] **Blog**: Write about trends, major incidents
- [ ] **Twitter/X**: Post daily updates
- [ ] **Media outreach**: Contact aviation/security journalists
- [ ] **Case studies**: Deep dives on major incidents

### 6.2 Partnerships
- [ ] **Aviation authorities**: Share data with FAA, EASA
- [ ] **Security researchers**: Collaborate on analysis
- [ ] **News organizations**: Provide data for reporting
- [ ] **Academic research**: Enable PhD research on drone threats

---

## Technical Debt & Maintenance

### Code Quality
- [ ] **Add tests**: Unit tests for API, scrapers
- [ ] **Type safety**: Strict TypeScript config
- [ ] **Documentation**: API docs, scraper architecture
- [ ] **Code review**: Establish review process

### Security
- [ ] **Rate limiting**: Prevent API abuse
- [ ] **Authentication**: API keys for external users
- [ ] **Input validation**: Sanitize all user inputs
- [ ] **HTTPS only**: Enforce secure connections

### Database
- [ ] **Migration system**: Track schema changes
- [ ] **Data validation**: Constraints on all fields
- [ ] **Archiving**: Move old incidents to archive table
- [ ] **Audit log**: Track all data modifications

---

## Success Metrics

### Short-term (1 Month)
- [ ] 50+ incidents in database
- [ ] Zero duplicates
- [ ] Scraper running reliably (>95% uptime)
- [ ] 3+ countries covered

### Medium-term (3 Months)
- [ ] 200+ incidents
- [ ] 5+ data sources
- [ ] 1000+ monthly visitors
- [ ] Media mentions

### Long-term (6+ Months)
- [ ] 500+ incidents
- [ ] 10+ countries
- [ ] Academic citations
- [ ] Industry partnerships

---

## Priority Queue (Next 2 Weeks)

**High Priority:**
1. ✅ Fix CORS/API issues (DONE!)
2. ✅ Clean up duplicates (SQL script provided)
3. [ ] Add unique constraint to prevent duplicates
4. [ ] Implement scraper duplicate detection
5. [ ] Add 2-3 more news sources (Norway, Sweden)

**Medium Priority:**
6. [ ] Add timeline slider to map
7. [ ] Create analytics dashboard
8. [ ] Write documentation for evidence levels
9. [ ] Set up error monitoring

**Low Priority:**
10. [ ] User submission form
11. [ ] Email notifications
12. [ ] Blog/content creation

---

## Resources Needed

### Development
- **Time**: 10-15 hours/week for active development
- **Tools**: Current stack is good (Next.js, Supabase, Vercel)
- **APIs**: Consider paid NOTAM feed if available

### Data
- **Sources**: More RSS feeds, official aviation authorities
- **Verification**: Cross-reference multiple sources
- **Quality**: Manual review of high-profile incidents

### Infrastructure
- **Costs**: Current (Vercel + Supabase free tier) should work for 10k+ incidents
- **Scaling**: May need paid tier at 50k+ requests/day
- **Backup**: External backup service when critical

---

## Notes
- Keep the focus on **evidence-based reporting**
- Avoid speculation - only verified incidents
- Maintain neutral, factual tone
- Prioritize data quality over quantity
- Build trust with aviation/security community

**Last Updated**: 2025-09-30
**Version**: 1.0