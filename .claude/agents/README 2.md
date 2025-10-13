# DroneWatch Specialized Subagents

This directory contains 5 specialized AI subagents for the DroneWatch project. Each subagent is an expert in a specific domain and will be automatically invoked by Claude Code when relevant tasks arise.

## Available Subagents

### 1. `dronewatch-frontend` - React/Next.js Expert
**Expertise**: Frontend debugging, React Query, environment variables, browser integration

**Auto-Activates When**:
- Issues with "0 incidents" or data not rendering
- React Query not fetching data
- Environment variable problems (NEXT_PUBLIC_API_URL)
- Browser vs. API discrepancies
- Map clustering or Leaflet issues

**Manual Invocation**:
```
Use dronewatch-frontend to debug why the incidents aren't displaying
Ask dronewatch-frontend to check the React Query configuration
```

**Tools**: Read, Write, Edit, Grep, Glob, Bash, WebFetch

---

### 2. `dronewatch-api` - Python API & PostGIS Expert
**Expertise**: API endpoints, database queries, incident data structures, serverless functions

**Auto-Activates When**:
- API returns wrong data or errors
- Database connection issues
- PostGIS spatial query problems
- Port confusion (5432 vs 6543)
- Missing incident sources

**Manual Invocation**:
```
Use dronewatch-api to check the PostGIS query
Ask dronewatch-api to validate the API endpoint response
```

**Tools**: Read, Write, Edit, Grep, Glob, Bash

---

### 3. `dronewatch-scraper` - Ingestion Pipeline Expert
**Expertise**: Multi-source consolidation, fake news detection, AI verification, evidence scoring

**Auto-Activates When**:
- Incidents not being ingested
- Duplicate incidents appearing
- Evidence scores incorrect
- Geographic filtering issues
- AI verification errors
- Consolidation problems

**Manual Invocation**:
```
Use dronewatch-scraper to check why incidents are being filtered out
Ask dronewatch-scraper to validate the evidence score calculation
```

**Tools**: Read, Write, Edit, Grep, Glob, Bash

---

### 4. `dronewatch-devops` - Deployment & Configuration Expert
**Expertise**: Vercel deployment, environment variables, production debugging

**Auto-Activates When**:
- Deployment fails
- Production behaves differently than local
- Environment variable issues
- Secrets exposed in frontend
- Build errors

**Manual Invocation**:
```
Use dronewatch-devops to check the Vercel configuration
Ask dronewatch-devops to validate environment variables
```

**Tools**: Read, Grep, Glob, Bash, WebFetch

---

### 5. `dronewatch-qa` - Testing & Quality Assurance Expert
**Expertise**: E2E testing (Playwright), test suite validation, browser automation, regression testing

**Auto-Activates When**:
- Code changes are made (runs tests)
- Before deployment (validation required)
- After deployment (smoke tests)
- Claiming a fix works (requires evidence)
- Browser testing needed

**Manual Invocation**:
```
Use dronewatch-qa to run the full test suite
Ask dronewatch-qa to validate the production deployment
Have dronewatch-qa test this fix in the browser
```

**Tools**: Read, Write, Edit, Grep, Glob, Bash, WebFetch

**Key Behavior**:
- ✅ Always requires browser testing before claiming success
- ✅ Runs Playwright for real user validation
- ✅ Enforces all quality gates before deployment
- ❌ Never allows deployment without test evidence

---

## How They Work

### Automatic Invocation
Claude Code will automatically delegate tasks to the appropriate subagent based on:
- Keywords in your request (e.g., "frontend", "API", "deployment")
- Context of the conversation (e.g., discussing React Query issues)
- Type of files being modified (e.g., editing `useIncidents.ts` → frontend expert)

### Manual Invocation
You can explicitly request a specific subagent:
```
Use dronewatch-frontend to...
Ask dronewatch-api to...
Have dronewatch-scraper check...
Get dronewatch-devops to verify...
```

### Coordination Between Subagents
Subagents can work together on complex issues:
- **Frontend + DevOps**: Environment variable issues affecting production
- **API + Scraper**: Data pipeline from ingestion to API response
- **Frontend + API**: End-to-end data flow debugging
- **DevOps + All**: Full deployment and production validation

## Key Features

### Domain-Specific Knowledge
Each subagent has deep knowledge of:
- Critical files and their purposes
- Common issues and solutions
- Code patterns and best practices
- Debugging workflows
- Quality standards

### Proactive Behavior
Subagents are configured to:
- ✅ Always validate environment variables
- ✅ Require browser testing before claiming fixes work
- ✅ Check logs and metrics
- ✅ Follow proper testing workflows
- ❌ Never skip validation steps
- ❌ Never claim success without evidence

### Consistent Quality
All subagents enforce:
- Evidence-based debugging (not assumptions)
- Browser testing for frontend issues (not just curl)
- Proper separation of frontend/backend secrets
- Following DroneWatch architecture patterns

## Usage Examples

### Example 1: Frontend Display Bug
```
User: "Production shows 0 incidents but the API works"

Claude: I'll use the dronewatch-frontend subagent to investigate this.
[dronewatch-frontend checks NEXT_PUBLIC_API_URL, React Query config, browser console]
```

### Example 2: Database Query Issue
```
User: "The API is returning incidents without coordinates"

Claude: Let me ask dronewatch-api to check the PostGIS query.
[dronewatch-api validates ST_Y/ST_X usage and database schema]
```

### Example 3: Deployment Problem
```
User: "Vercel deployment succeeded but site is broken"

Claude: I'll have dronewatch-devops validate the deployment.
[dronewatch-devops checks env vars, logs, and browser behavior]
```

### Example 4: Complex Multi-Domain Issue
```
User: "New incidents aren't appearing on the map"

Claude: This involves multiple systems. I'll coordinate:
- dronewatch-scraper to check ingestion pipeline
- dronewatch-api to verify database storage
- dronewatch-frontend to check display logic
[Subagents work together to trace the full data flow]
```

## Benefits

### Faster Debugging
- Each subagent has specialized knowledge of its domain
- No need to context-switch between different areas
- Immediate access to relevant troubleshooting steps

### Consistent Quality
- Enforced best practices across all domains
- Standardized debugging workflows
- Quality gates prevent common mistakes

### Better Documentation
- Each subagent documents its reasoning and findings
- Creates reusable knowledge base
- Helps onboard new developers

### Comprehensive Coverage
- Four domains cover entire DroneWatch stack
- No gaps in expertise or tooling
- Coordinated approach to complex issues

---

## Maintenance

To update a subagent:
1. Edit the corresponding `.md` file in this directory
2. Update the system prompt in the `---` delimited section
3. Changes take effect immediately (no restart needed)

To add a new subagent:
1. Create a new `.md` file: `dronewatch-{domain}.md`
2. Follow the same YAML frontmatter structure
3. Define clear responsibilities and triggers

---

**Created**: October 9, 2025
**Version**: 1.0.0
**DroneWatch Version**: 2.3.0
