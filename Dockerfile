FROM python:3.13-slim

ARG USER
ARG USER_ID
ARG GROUP
ARG GROUP_ID

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

RUN groupadd -g ${GROUP_ID} ${GROUP} \
    && useradd -u ${USER_ID} -g ${GROUP} ${USER} -d /home/${USER} -m -s /usr/bin/bash

WORKDIR /backlogforgames/app
