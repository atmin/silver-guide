PYTHON  = .venv/bin/python
DJANGO  = $(PYTHON) manage.py
PYTEST  = .venv/bin/pytest
DOCKER ?= docker

.PHONY: install migrate makemigrations dev up down reset-db logs test shell superuser seed seed-docker

# Create virtual environment and install dependencies
install:
	uv venv --python 3.14
	uv pip install -r requirements.txt

# Apply pending migrations (local dev, requires DB running)
migrate:
	$(DJANGO) migrate

# Generate migrations; optionally pass APP=catalog NAME=category
makemigrations:
	$(DJANGO) makemigrations $(APP)$(if $(NAME), --name $(NAME),)

# Start DB in Docker, wait for it to accept connections, then run dev server locally
dev:
	$(DOCKER) compose up db -d
	$(PYTHON) wait_for_db.py
	$(DJANGO) runserver

# Start full stack in Docker (rebuilds image if changed)
up:
	$(DOCKER) compose up --build

# Stop all Docker services and remove containers
down:
	$(DOCKER) compose down

# WARNING: destroys all data — stops containers and deletes the db volume
reset-db:
	@echo "WARNING: this will delete all data in the database volume."
	@read -p "Type 'yes' to confirm: " confirm && [ "$$confirm" = "yes" ]
	$(DOCKER) compose down -v

# Tail logs; optionally pass SERVICE=web or SERVICE=db
logs:
	$(DOCKER) compose logs -f $(SERVICE)

# Run test suite (local, requires DB running)
test:
	$(PYTEST)


# Run tests via Docker (no local venv needed); starts db automatically
test-docker:
	$(DOCKER) compose up db -d
	$(DOCKER) compose run web sh -c "python wait_for_db.py && pytest"

# Open Django shell (local)
shell:
	$(DJANGO) shell

# Create a Django superuser (local, interactive)
superuser:
	$(DJANGO) createsuperuser

# Seed the database with sample data; pass FLUSH=1 to wipe first
seed:
	$(DJANGO) seed $(if $(FLUSH),--flush,)

# Seed via Docker (no local venv needed); pass FLUSH=1 to wipe first
seed-docker:
	$(DOCKER) compose up db -d
	$(DOCKER) compose run web sh -c "python wait_for_db.py && python manage.py seed $(if $(FLUSH),--flush,)"
