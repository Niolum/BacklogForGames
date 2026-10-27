# Backlog For Games

API for a personal game list. A user keeps games they plan to play, marks games they have finished, rates finished games, and leaves comments on catalog games.

[![Python](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://coverage.readthedocs.io/)

## Features

- Accounts with email confirmation, a public profile, and an avatar.
- A game catalog with genres, covers, and search. The catalog is filled by an import from RAWG and by an admin panel.
- A personal backlog and a completed list. Each game belongs to one of the two lists.
- Scores from 1 to 10 for finished games. The game card shows the average and the caller's own score.
- Comments on a game: a visitor can read them, and a signed-in user can add, edit, and delete their own.

## Stack

- Python 3.13
- FastAPI, Pydantic v2, pydantic-settings
- PostgreSQL 17, SQLAlchemy 2.1 (async), asyncpg, Alembic
- Poetry
- PyJWT, bcrypt
- SQLAdmin
- aiofiles and aioboto3 for file storage
- pytest, pytest-cov, ruff, and mypy

## Requirements

Install these before running the project:

- [Python 3.13](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL 17](https://www.postgresql.org/)


## Fast start
### 1. Clone project

``` 
git clone https://github.com/Niolum/BacklogForGames.git
```

### 2. Permissions for `/opt/staraster`

Create the directories and assign them to your user:

```bash
sudo mkdir /opt/staraster
sudo chown -R "$USER:$USER" /opt/staraster
```
### 3. Setting up environment variables

Create a `.env` file in the repository root and populate it with your environment variables, using the `.example.env` file as a template:

```env
USER=developer
GROUP=developer

APP_CONFIG__ENVIRONMENT=development
APP_CONFIG__DB_ALEMBIC_URL=postgresql+asyncpg://postgres:password@backlogdb:5432/backlog_app

EMAIL_CONFIG__PASSWORD=smpt_password
EMAIL_CONFIG__USERNAME=smpt_username
EMAIL_CONFIG__HOST=smpt_host
EMAIL_CONFIG__PORT=smpt_port
EMAIL_CONFIG__FROM_EMAIL=smpt_from_email

RAWG_CONFIG__API_KEY=your_rawg_api_key
```

The `USER` and `GROUP` values must correspond to your system user (they are used when building the image).

### 4. Launching containers

Run from the repository root:

```bash
docker compose up -d --build
```

Services are starting up:

| Container | Purpose |
|-----------|------------|
| `backlogdb-postgres` | Application database |
| `web-backlog` | Main application |

### 5. Database initialization

Create the schemas required for Alembic migrations:
```bash
docker exec backlogdb-postgres psql -U postgres -d backlog_app -c 'create schema if not exists backlog_app'
docker exec backlogdb-postgres psql -U postgres -d backlog_app -c 'create schema if not exists infra'
```
or run:
```bash
make schemas_create
```

### 6. Alembic migration

Apply the application schema migrations:
```bash
docker exec web-backlog alembic upgrade head
```
or run:
```bash
make migrate
```

### 7. Examination

Ensure that the containers are running:

```bash
docker compose ps
```

Check the API's availability (the default port is `8000`):

```bash
curl http://localhost:8000/docs
```

## Run test

To run all the tests of a project, simply run the pytest command:
```bash
pytest
```

Run code coverage analysis in Python using pytest-cov:
```bash
pytest --cov --cov-report=html -sv app/tests/
```
or run:
```bash
make tests-coverage-html
```
