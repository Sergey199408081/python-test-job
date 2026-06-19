FROM python:3.14-slim

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root

COPY . .

RUN poetry install --without dev

EXPOSE 8000

CMD ["poetry", "run", "python", "-m", "app.main"]