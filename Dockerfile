FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-install-project

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini README.md ./

ENV PYTHONPATH=/app/src

RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "notification_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
