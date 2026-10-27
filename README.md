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
- pytest, ruff, and mypy

## Requirements

Install these before running the project:

- [Python 3.13](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL 17](https://www.postgresql.org/)
