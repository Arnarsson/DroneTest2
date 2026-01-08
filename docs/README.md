# DroneWatch 2.0 Documentation

**Real-time drone incident tracking across Europe with evidence-based reporting and multi-source verification.**

📍 **Geographic Coverage**: 35-71°N, -10-31°E (Nordic + UK + Ireland + Germany + France + Spain + Italy + Poland + Benelux + Baltics)
🔗 **Live Site**: https://dronewatch.cc → https://www.dronemap.cc
📊 **Version**: 2.3.0 (European Coverage Expansion)

---

## 📚 Documentation Structure

### 🚀 Getting Started

- [**Main README**](../README.md) - Project overview, quick start, tech stack
- [**Installation Guide**](setup/INSTALLATION.md) - Local development setup (TODO)
- [**Twitter RSS Setup**](setup/TWITTER_RSS_SETUP.md) - Configure police Twitter feeds

### 🏗️ Architecture

- [**Product Requirements**](architecture/PRD.md) - System requirements and specifications
- [**Multi-Layer Defense**](architecture/MULTI_LAYER_DEFENSE.md) - 5-layer validation system
- [**AI Verification**](architecture/AI_VERIFICATION.md) - OpenRouter/OpenAI integration (v2.2.0)
- [**Database Schema**](architecture/DATABASE.md) - PostGIS schema and migrations (TODO)

### 💻 Development

#### Frontend (Next.js 14)
- [**Frontend Guide**](development/frontend/README.md) - React/TypeScript, components, pages
- [**Evidence System**](development/frontend/EVIDENCE.md) - 4-tier scoring system (TODO)
- [**Map Component**](development/frontend/MAP.md) - Leaflet integration, clustering (TODO)

#### Backend (Python Serverless)
- [**Backend API**](development/backend/README.md) - Python serverless functions, PostGIS queries
- [**API Reference**](development/backend/API.md) - Endpoint documentation (TODO)
- [**API Rate Limiting**](API_RATE_LIMITING.md) - Rate limits, headers, and Upstash Redis setup

#### Ingestion (Python 3.11)
- [**Ingestion System**](development/ingestion/README.md) - Scrapers, validation, consolidation
- [**Source Configuration**](development/ingestion/SOURCES.md) - RSS feeds, trust weights (TODO)
- [**Geographic Filter**](development/ingestion/GEOGRAPHIC.md) - European bounds validation (TODO)

### 🧪 Testing

- [**Testing Guide**](testing/README.md) - Test suites, validation scripts
- [**Test Reports**](testing/REPORTS.md) - Test results and coverage (TODO)

### 📦 Archive

- [**Historical Docs**](archive/) - Session summaries, old deployment reports (Oct 7, 2025)

---

## 🎯 Quick Navigation

### For New Developers

1. **Start here**: [Main README](../README.md)
2. **Setup dev environment**: [Installation Guide](setup/INSTALLATION.md)
3. **Understand architecture**: [Multi-Layer Defense](architecture/MULTI_LAYER_DEFENSE.md)
4. **Read component docs**: [Frontend](development/frontend/), [Backend](development/backend/), [Ingestion](development/ingestion/)

### For Contributors

- **Frontend changes**: See [Frontend Guide](development/frontend/README.md)
- **Backend API**: See [Backend API](development/backend/README.md)
- **Add sources**: See [Source Configuration](development/ingestion/SOURCES.md)
- **Run tests**: See [Testing Guide](testing/README.md)

### For Maintainers

- **Database migrations**: `migrations/` directory + [Database Schema](architecture/DATABASE.md)
- **Deployment**: [Main README](../README.md) → Deployment section
- **AI instructions**: [CLAUDE.md](../CLAUDE.md) (root directory)

---

## 🔑 Key Concepts

### Evidence System (4-Tier)
- **Score 4 (OFFICIAL)**: Police, military, NOTAM, aviation authority
- **Score 3 (VERIFIED)**: 2+ media sources WITH official quotes
- **Score 2 (REPORTED)**: Single credible source (trust_weight ≥ 2)
- **Score 1 (UNCONFIRMED)**: Social media, low trust sources

### Multi-Layer Defense (5 Layers)
1. **Database Trigger**: PostgreSQL geographic validation (35-71°N, -10-31°E)
2. **Python Filters**: Keyword-based validation in `ingestion/utils.py`
3. **AI Verification**: OpenRouter/OpenAI incident classification (v2.2.0)
4. **Cleanup Jobs**: Automated foreign incident removal
5. **Monitoring**: Real-time system health metrics

### Geographic Coverage
- **European Bounds**: 35-71°N, -10-31°E
- **Includes**: Nordic, UK, Ireland, Germany, France, Spain, Italy, Poland, Benelux, Baltics
- **Blocks**: Ukraine, Russia, Belarus, Middle East, Asia, Americas, Africa

---

## 📞 Support

- **Issues**: https://github.com/Arnarsson/DroneWatch2.0/issues
- **Live Site**: https://www.dronemap.cc
- **API Docs**: Coming soon

---

**Last Updated**: October 9, 2025
**Version**: 2.3.0 (European Coverage Expansion)
