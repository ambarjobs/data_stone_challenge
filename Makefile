SHELL=/bin/bash

include .env

POSTGRESQL_SETUP_DELAY = 10

# ==================================================================================================
#  Build commands
# --------------------------------------------------------------------------------------------------
.PHONY: validate_env
validate_env: ## Validate docker environment requirements.
	@command -v docker > /dev/null || (echo "You need to install docker before proceeding" && exit 1)
	@command -v docker-compose > /dev/null || (echo "You need to install docker-compose before proceeding" && exit 1)

# --------------------------------------------------------------------------------------------------
.PHONY: build
build: validate_env ## Build images and start the containers.

	@docker-compose stop
# Build the custom image.
	@docker-compose build
# Start postgresql container
	@docker-compose up -d postgresql
# Prompt to wait PostgreSQL set up.
	@echo "Waiting for PostgreSQL setting up ..."
	@sleep $(POSTGRESQL_SETUP_DELAY)
# Initialize PostgreSQL
	@docker-compose exec postgresql ./init_postgresql
# Start remaining containers
	@docker-compose up -d
# Make initial migrations
	@docker-compose exec app ./manage.py migrate

# --------------------------------------------------------------------------------------------------
.PHONY: reset-build
reset-build: ## Remove build's containers and images.
	@docker-compose stop
	@docker rm -v ds-app ds-db ds-redis

# --------------------------------------------------------------------------------------------------
.PHONY: reset-containers
reset-containers: ## Destroy and recreate all containers from last built images.
	@docker-compose down
	@docker-compose up -d

# --------------------------------------------------------------------------------------------------
.PHONY: remove-all
remove: ## Remove all containers and wipe all data
	@docker-compose down

# ==================================================================================================
#  General commands
# --------------------------------------------------------------------------------------------------
all:
	@echo "Try 'make help'"

# --------------------------------------------------------------------------------------------------
.PHONY: help
help: ## Makefile help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

# --------------------------------------------------------------------------------------------------
.PHONY: start
start: ## Start containers.
	@docker-compose up -d

# --------------------------------------------------------------------------------------------------
.PHONY: stop
stop: ## Stop containers.
	@docker-compose stop

# --------------------------------------------------------------------------------------------------
.PHONY: restart
restart: ## Restart all containers
	@docker-compose stop
	@sleep 3
	@docker-compose up -d

.DEFAULT_GOAL := help

# --------------------------------------------------------------------------------------------------
.PHONY: status
status: ## Show status of the containers.
	@docker-compose ps --format 'table {{.Name}}\t{{.Service}}\t{{.Status}}'

# ==================================================================================================
#  App commands
# --------------------------------------------------------------------------------------------------
.PHONY: logs service
logs: ## Show status of the containers.
	@docker-compose logs -t -f ${service}

# --------------------------------------------------------------------------------------------------
.PHONY: app_status
app_status: ## Show status of the app container.
	@docker inspect ds-app --format "{{.State.Status}}"

# --------------------------------------------------------------------------------------------------
.PHONY: inside
inside: ## Reach OS shell inside app container.
	@docker-compose exec -it app /bin/bash

# --------------------------------------------------------------------------------------------------
.PHONY: delete_bytecode
delete_bytecode: # Remove Python bytecode compiled files
	@docker-compose exec app find . -name "*.pyc" -delete
	@docker-compose exec app find . -name "__pycache__" -delete

# --------------------------------------------------------------------------------------------------
.PHONY: test class test_name module
test: # Execute test suite, optionally restricted to a `class`, `test_name` or `module`.
ifdef test_name
	@docker-compose exec app pytest ${module}/tests.py::${class}::${test_name}
else ifdef class
	@docker-compose exec app pytest ${module}/tests.py::${class}
else ifdef module
	@docker-compose exec app pytest -k ${module}
else
	@docker-compose exec app pytest
endif

# ==================================================================================================
#  Django commands
# --------------------------------------------------------------------------------------------------
.PHONY: makemigrations
makemigrations: ## Generate migrations.
	@docker-compose exec app ./manage.py makemigrations

# --------------------------------------------------------------------------------------------------
.PHONY: migrate app
migrate: ## Apply migrations.
	@docker-compose exec app ./manage.py migrate $(app)

# --------------------------------------------------------------------------------------------------
.PHONY: showmigrations app
showmigrations: ## Show current migrations status.
	@docker-compose exec app ./manage.py showmigrations $(app)
# --------------------------------------------------------------------------------------------------
.PHONY: shell
shell: ## Django shell inside app container.
	@docker-compose exec app ./manage.py shell

# ==================================================================================================
#  PostgreSQL commands
# --------------------------------------------------------------------------------------------------
.PHONY: inside-db
inside-db: ## Reach OS shell inside PostgreSQL container.
	@docker-compose exec -it postgresql /bin/bash

# --------------------------------------------------------------------------------------------------
.PHONY: init-db
init-db: ## Initialize PostgreSQL (ERASE all data) and create app user.
	@docker-compose exec postgresql ./init_postgresql
