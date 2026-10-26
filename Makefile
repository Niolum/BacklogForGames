schemas_create:
	docker exec backlogdb-postgres psql -U postgres -d backlog_app -c 'create schema if not exists backlog_app'
	docker exec backlogdb-postgres psql -U postgres -d backlog_app -c 'create schema if not exists infra'

migrate:
	docker exec web-backlog alembic upgrade head

tests-coverage-html:
	pytest --cov --cov-report=html -sv app/tests/
