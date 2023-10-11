######################################
# Base image
######################################
FROM python:3.11.2-slim as python-base
ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    SETUP_PATH="/var/www/backend" \
    VENV_PATH="/var/www/backend/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
######################################
# Builder image
######################################
FROM python-base as builder-base
RUN apt update && \
    apt install -y --no-install-recommends \
    build-essential \
    curl
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"
WORKDIR $SETUP_PATH
COPY ../poetry.lock ../pyproject.toml ./
RUN poetry install --no-root --only main
COPY ../src ./src
######################################
# Prod image
######################################
FROM python-base as production
WORKDIR $SETUP_PATH
COPY --from=builder-base $SETUP_PATH $SETUP_PATH
CMD uvicorn src.main:app --host=0.0.0.0 --port=8080 --workers=1
