FROM ubuntu:24.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt update && apt -y install curl && apt -y upgrade && curl https://install.duckdb.org | sh

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . ./
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:/root/.duckdb/cli/latest:$PATH"
ENV DAGSTER_HOME="/app/.dagster"

EXPOSE 3000

CMD ["uv", "run", "dg", "dev", "--host", "0.0.0.0", "--port", "3000"]
