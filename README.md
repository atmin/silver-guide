# Catalog API

E-commerce product catalogue service — categories with tree hierarchy and products with search and filtering.

## Prerequisites

- **Docker and Docker Compose** — for MariaDB (and optionally the full stack). Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Podman Desktop](https://podman-desktop.io/) on Mac/Windows.
- **uv** — Python package manager, needed for local dev mode only:
  ```bash
  brew install uv
  # or
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Quickstart — Full Docker

No local Python required.

```bash
cp .env.example .env
make up
```

- App: http://localhost:8000
- Admin: http://localhost:8000/admin/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/

To seed sample data:

```bash
make seed-docker
make seed-docker FLUSH=1   # wipe and re-seed
```

## Local Dev — DB in Docker, app on host

Preferred for active development: faster restarts, local debugger, no rebuilds.

```bash
cp .env.example .env          # DB_HOST is already set to 127.0.0.1
make up db                    # start MariaDB only
make install                  # create .venv/ and install dependencies
make migrate                  # apply migrations
make superuser                # create admin user (interactive)
make dev                      # wait for DB, then start dev server
```

To seed the database with sample data:

```bash
make seed           # idempotent
make seed FLUSH=1   # wipe and re-seed
```

## Running Tests

Tests use a separate `test_catalog` database created automatically by pytest-django.

```bash
make test

# or via Docker
make test-docker
```

## API

| URL | Description |
|-----|-------------|
| http://localhost:8000/api/schema/swagger-ui/ | Swagger UI |
| http://localhost:8000/api/schema/redoc/ | ReDoc |
| http://localhost:8000/api/schema/ | Raw OpenAPI 3.0 schema (YAML) |
| http://localhost:8000/api/v1/ | API base |

### Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET, POST | `/api/v1/categories/` | List / create categories |
| GET, PUT, PATCH, DELETE | `/api/v1/categories/{id}/` | Retrieve / update / delete a category |
| GET, POST | `/api/v1/products/` | List / create products |
| GET, PUT, PATCH, DELETE | `/api/v1/products/{id}/` | Retrieve / update / soft-delete a product |

Write operations (POST, PUT, PATCH, DELETE) require a session-authenticated user — log in via the Django admin at `/admin/` with the superuser created by `make superuser`.

### Product search — `GET /api/v1/products/`

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Title or SKU substring, case-insensitive |
| `sku` | string | Exact SKU match, case-insensitive |
| `category_id` | integer | Products in this category and all descendants |
| `category_slug` | string | Same as `category_id` but by slug |
| `price_min` | decimal | Minimum price (inclusive) |
| `price_max` | decimal | Maximum price (inclusive) |
| `ordering` | string | Sort field: `price`, `created_at`, `title`. Prefix with `-` for descending |

Example:

```bash
curl "http://localhost:8000/api/v1/products/?category_slug=hrani-mlechni&price_max=4.00&ordering=price"
```

## Models

### Category

Tree structure via a self-referential `parent` FK (adjacency list). Descendant traversal is done with an in-memory BFS — efficient for trees that fit in memory (hundreds of nodes). See [ADR-0002](docs/adr/0002_category_tree_model.md).

### Product

Key fields: `sku` (unique business key), `title`, `price`, `category`, `is_active`.

`DELETE /api/v1/products/{id}/` does not remove the row — it sets `is_active=False` (soft delete). Inactive products are excluded from all list and filter results. See [ADR-0003](docs/adr/0003_product_model.md).
