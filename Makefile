schemas_create:
	docker exec backlogdb-postgres psql -U postgres -d backlog_app -c 'create schema if not exists backlog_app'
	docker exec backlogdb-postgres psql -U postgres -d backlog_app -c 'create schema if not exists infra'
