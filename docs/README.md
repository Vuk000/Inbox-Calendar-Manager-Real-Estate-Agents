# RealInbox AI - Documentation Index

Complete documentation for the RealInbox AI platform.

---

## 📚 Essential Documentation

### Getting Started
- **[Main README](../README.md)** - Project overview and quick start
- **[Project Status](../PROJECT_STATUS.md)** - Current implementation status
- **[Developer Setup](../DEVELOPER_SETUP.md)** - Complete setup guide
- **[Architecture](../ARCHITECTURE.md)** - System design and technical decisions

---

## 🔧 Guides

### Development
- **[Migration Guide](guides/MIGRATION_GUIDE.md)** - Database migrations with Alembic
- **[Testing Checklist](guides/TESTING_CHECKLIST.md)** - Test coverage and quality

### Deployment
- **[Deployment Checklist](guides/DEPLOYMENT_CHECKLIST.md)** - Production deployment steps
- **[Environment Variables](../backend/ENV_TEMPLATE.md)** - Configuration reference

---

## 📦 Component Documentation

### Backend
- **[Backend README](../backend/README.md)** - Python/FastAPI backend
- **[API Documentation](http://localhost:8000/api/v1/docs)** - Interactive API docs (when running)
- **[Models](../backend/app/models/)** - Database models
- **[Routers](../backend/app/routers/)** - API endpoints
- **[Services](../backend/app/services/)** - Business logic
- **[Agents](../backend/app/agents/)** - AI agents

### Frontend
- **[Frontend README](../frontend/README.md)** - React/TypeScript frontend
- **[Components](../frontend/src/components/)** - UI components
- **[Pages](../frontend/src/pages/)** - Page components
- **[Types](../frontend/src/types/)** - TypeScript definitions

---

## 📋 Reference

### Architecture
- **Tech Stack**: FastAPI, React, SQLAlchemy, Anthropic Claude
- **Database**: PostgreSQL (prod) / SQLite (dev)
- **State Management**: Zustand (frontend)
- **AI**: Claude Sonnet 4.5 for email triage and drafting

### Key Features
1. **CRM Core**: Contact management with unified timeline
2. **Email Management**: Multi-account sync (Gmail, Outlook)
3. **AI Agents**: Triage, drafting, lead qualification
4. **Transaction Pipeline**: Deal management with stages
5. **Team Collaboration**: Shared contacts and workflows

---

## 📜 Historical Documentation

Archived documentation from previous phases:
- **[Archive](archive/)** - Historical status reports and phase documentation

---

## 🆘 Getting Help

1. **Check Project Status**: See what's working and known issues
2. **Read Setup Guide**: Step-by-step instructions
3. **Check Architecture**: Understanding system design
4. **Review Guides**: Specific tasks and operations

---

**Last Updated**: October 25, 2025

