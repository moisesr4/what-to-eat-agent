COMPOSE := docker compose
AIRFLOW_SERVICES := postgres airflow-api-server airflow-scheduler airflow-triggerer airflow-dag-processor

.PHONY: help \
        airflow-bootstrap airflow-init airflow-up airflow-down \
        airflow-restart airflow-logs airflow-clean airflow-ps airflow-shell

# ── Help ──────────────────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ── Airflow ───────────────────────────────────────────────────────────────────

airflow-bootstrap: ## First-time setup: DB migration + admin user + start services
	$(MAKE) airflow-init
	$(MAKE) airflow-up

airflow-init: ## Run DB migration and create admin user (run once, before airflow-up)
	@echo "→ Migrating Airflow DB and creating admin user…"
	$(COMPOSE) up --exit-code-from airflow-init airflow-init
	@echo "✓ Init complete. Run 'make airflow-up' to start services."

airflow-up: ## Start all Airflow services in the background
	@echo "→ Starting Airflow 3 (UI → http://localhost:8080)…"
	$(COMPOSE) up -d $(AIRFLOW_SERVICES)

airflow-down: ## Stop and remove all containers
	@echo "→ Stopping Airflow stack…"
	$(COMPOSE) down

airflow-restart: ## Restart Airflow services (volumes stay intact)
	$(COMPOSE) restart airflow-api-server airflow-scheduler airflow-triggerer airflow-dag-processor

airflow-logs: ## Follow logs of all Airflow services
	$(COMPOSE) logs -f airflow-api-server airflow-scheduler airflow-triggerer airflow-dag-processor

airflow-clean: ## Stop containers and delete all volumes (full reset)
	@echo "→ Removing all containers and volumes…"
	$(COMPOSE) down -v --remove-orphans

airflow-ps: ## Show status of all containers
	$(COMPOSE) ps

airflow-shell: ## Open a bash session inside the api-server container
	$(COMPOSE) exec airflow-api-server bash
