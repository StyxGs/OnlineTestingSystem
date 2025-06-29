FROM python:3.11.6-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONBUFFERED 1

RUN pip install poetry==1.7.1

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --with main --no-ansi --no-root

COPY src/ .
