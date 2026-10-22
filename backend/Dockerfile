FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libgles2 libegl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=secret,id=ca_bundle \
    if [ -f /run/secrets/ca_bundle ]; then SSL_CERT_FILE=/run/secrets/ca_bundle uv sync --frozen --no-dev; else uv sync --frozen --no-dev; fi
ENV PATH="/app/backend/.venv/bin:$PATH"
COPY backend ./
RUN useradd -m spvs && chown -R spvs:spvs /app
USER spvs
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
