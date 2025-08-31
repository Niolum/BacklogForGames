FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y gcc libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backlogforgames

COPY pyproject.toml /backlogforgames/

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . /backlogforgames/

WORKDIR /backlogforgames/app