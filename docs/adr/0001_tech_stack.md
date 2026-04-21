# ADR-0001: Tech Stack Selection

## Status

Accepted

## Context

Need a production-ready REST API service for e-commerce product/category management.
Primary goals: clarity, maintainability, confidence, extendability over novelty.

## Decision

Django + Django REST Framework + MariaDB.

## Alternatives considered

- **FastAPI + SQLAlchemy + Alembic**: more flexible, but that flexibility is a cost here —
  pagination, filtering, admin UI, and migration tooling would all need assembling from
  scratch. No equivalent of Django Admin. Right choice if async I/O or external service
  calls were the bottleneck; they are not.
- **PostgreSQL instead of MariaDB**: marginally better full-text search and richer column
  types, but the design uses no PostgreSQL-specific features. MariaDB matches company
  infrastructure.
- **SQLite for local dev**: ruled out because local and production environments must run
  the same database engine. SQLite differences — type affinity (DECIMAL stored as float),
  single-writer locking, case-sensitivity edge cases — create bugs that are invisible
  locally and only surface in production. MariaDB in Docker costs one command.

## Consequences

- Django Admin provides a free operational UI with no additional code.
- `django-filter` + DRF covers the search/filter endpoint declaratively.
- Sync worker model (gunicorn) is sufficient; horizontal scaling and a read replica are
  the natural growth path if needed.
- Team must be comfortable with Django conventions; onboarding cost is offset by the
  volume of solved problems the framework brings.
